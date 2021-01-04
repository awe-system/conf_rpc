package trace_rpc

import (
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"github.com/goinggo/workpool"
	"io"
	"log"
	"net"
	"reflect"
	"runtime"
	"sync"
	"time"
	"unsafe"
)

func _log_info(a ...interface{}) (n int, err error) {
	return fmt.Println(a)
}

func _log_debug(a ...interface{}) (n int, err error) {
	//return fmt.Println(a)
	return 0, nil
}

func SizeStruct(data interface{}) (int, error) {
	return sizeof(reflect.ValueOf(data))
}

func sizeof(v reflect.Value) (int, error) {
	switch v.Kind() {
	case reflect.Map:
		sum := 0
		keys := v.MapKeys()
		for i := 0; i < len(keys); i++ {
			mapkey := keys[i]
			s, err := sizeof(mapkey)
			if s < 0 {
				return -1, err
			}
			sum += s
			s, err = sizeof(v.MapIndex(mapkey))
			if s < 0 {
				return -1, err
			}
			sum += s
		}
		return sum, nil
	case reflect.Slice, reflect.Array:
		sum := 0
		for i, n := 0, v.Len(); i < n; i++ {
			s, err := sizeof(v.Index(i))
			if s < 0 {
				return -1, err
			}
			sum += s
			//sum += 8
		}
		// add 8 bytes to store length
		sum += 8
		return sum, nil

	case reflect.String:
		sum := 1
		for i, n := 0, v.Len(); i < n; i++ {
			s, err := sizeof(v.Index(i))
			if s < 0 {
				return -1, err
			}
			sum += s
		}
		return sum, nil

	case reflect.Ptr, reflect.Interface:
		p := (*[]byte)(unsafe.Pointer(v.Pointer()))
		if p == nil {
			return 0, errors.New("ptr is nil")
		}
		return sizeof(v.Elem())
	case reflect.Struct:
		sum := 0
		for i, n := 0, v.NumField(); i < n; i++ {
			s, err := sizeof(v.Field(i))
			if s < 0 {
				return -1, err
			}
			sum += s
		}
		return sum, nil

	case reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64,
		reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64,
		reflect.Float32, reflect.Float64, reflect.Complex64, reflect.Complex128,
		reflect.Int:
		return int(v.Type().Size()), nil

	default:
		return -1, errors.New("type not support")
	}

}

func Encode(data interface{}, res *bytes.Buffer) error {

	return encode(reflect.ValueOf(data), res)

}

func encode(v reflect.Value, res *bytes.Buffer) error {

	switch v.Kind() {
	case reflect.Slice, reflect.Array:
		dataLength := len(v.Bytes())
		_log_debug("dataLength:", dataLength)
		err := binary.Write(res, binary.LittleEndian, uint64(dataLength))
		if err != nil {
			return err
		}

		err = binary.Write(res, binary.LittleEndian, v.Bytes())
		if err != nil {
			return err
		}
		return nil

	case reflect.String:
		buf := []byte(v.String())
		buf = append(buf, 0)
		err := binary.Write(res, binary.LittleEndian, buf)
		if err != nil {
			return err
		}
		return nil

	case reflect.Struct:
		for i, n := 0, v.NumField(); i < n; i++ {
			err := encode(v.Field(i), res)
			if err != nil {
				return err
			}
		}
		return nil

	case reflect.Uint64:
		err := binary.Write(res, binary.LittleEndian, uint64(v.Uint()))
		if err != nil {
			return err
		}
		return nil
	case reflect.Uint32:
		err := binary.Write(res, binary.LittleEndian, uint32(v.Uint()))
		if err != nil {
			return err
		}
		return nil

	case reflect.Int32:
		err := binary.Write(res, binary.LittleEndian, int32(v.Int()))
		if err != nil {
			return err
		}
		return nil

	case reflect.Int:
		err := binary.Write(res, binary.LittleEndian, int(v.Int()))
		if err != nil {
			return err
		}
		return nil

	case reflect.Int64:
		err := binary.Write(res, binary.LittleEndian, v.Int())
		if err != nil {
			return err
		}
		return nil

	default:
		_log_info("t.Kind() no found:", v.Kind())
		return errors.New("type no found")
	}

}

func Decode(response interface{}, recData []byte) error {

	t := reflect.TypeOf(response)
	if t.Name() != "" {
		return fmt.Errorf("result have to be a point")
	}
	v := reflect.ValueOf(response).Elem()
	t = v.Type()

	num := 0
	for i, n := 0, v.NumField(); i < n; i++ {

		switch v.Field(i).Kind() {
		case reflect.Slice, reflect.Array:
			dataStart := num + 8
			dataLengthBuff := bytes.NewBuffer(recData[num:dataStart])
			var dataLength uint64
			err := binary.Read(dataLengthBuff, binary.LittleEndian, &dataLength)
			if err != nil {
				return err
			}
			num = dataStart + int(dataLength)
			v.FieldByName(t.Field(i).Name).SetBytes(recData[dataStart:num])
		case reflect.String:
			index := bytes.IndexByte(recData[num:], 0)

			v.FieldByName(t.Field(i).Name).SetString(string(recData[num : num+index]))
			num = num + index + 1

		//case reflect.Uint8, reflect.Uint16, reflect.Uint64,
		//	reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64,
		//	reflect.Float32, reflect.Float64, reflect.Complex64, reflect.Complex128,
		//	reflect.Int:

		case reflect.Int64:
			var data int64
			size, _ := sizeof(reflect.ValueOf(data))
			byteBuff := bytes.NewBuffer(recData[num : num+size])

			err := binary.Read(byteBuff, binary.LittleEndian, &data)
			if err != nil {
				return err
			}
			v.FieldByName(t.Field(i).Name).SetInt(data)
			num = num + size

		case reflect.Int32:
			var data int32
			size, _ := sizeof(reflect.ValueOf(data))
			byteBuff := bytes.NewBuffer(recData[num : num+size])

			err := binary.Read(byteBuff, binary.LittleEndian, &data)
			if err != nil {
				return err
			}
			v.FieldByName(t.Field(i).Name).SetInt(int64(data))
			num = num + size

		case reflect.Int:
			var data int
			size, _ := sizeof(reflect.ValueOf(data))
			byteBuff := bytes.NewBuffer(recData[num : num+size])

			err := binary.Read(byteBuff, binary.LittleEndian, &data)
			if err != nil {
				return err
			}
			v.FieldByName(t.Field(i).Name).SetInt(int64(data))
			num = num + size

		case reflect.Uint32:
			var data uint32
			size, _ := sizeof(reflect.ValueOf(data))
			byteBuff := bytes.NewBuffer(recData[num : num+size])

			err := binary.Read(byteBuff, binary.LittleEndian, &data)
			if err != nil {
				return err
			}
			v.FieldByName(t.Field(i).Name).SetUint(uint64(data))
			num = num + size

		case reflect.Uint64:
			var data uint64
			size, _ := sizeof(reflect.ValueOf(data))
			byteBuff := bytes.NewBuffer(recData[num : num+size])

			err := binary.Read(byteBuff, binary.LittleEndian, &data)
			if err != nil {
				return err
			}
			v.FieldByName(t.Field(i).Name).SetUint(data)
			num = num + size

		default:
			_log_info("t.Kind() no found:", v.Field(i).Kind())
			return errors.New("type no found")
		}
	}
	return nil

}

type CallBackFunc func(param interface{}, reply interface{}, err error)

// Call represents an active RPC.
type Call struct {
	ServiceMethod string      // The name of the service and method to call.
	Req           interface{} // The argument to the function (*struct).
	Reply         interface{} // The reply from the function (*struct).
	Error         error       // After completion, the error status.
	Done          chan *Call  // Strobes when call is complete.
	Callback      CallBackFunc
	Param         interface{}
	WP            *workpool.WorkPool
}

func (call *Call) done() {
	select {
	case call.Done <- call:
		// ok call user's func
		if call.Callback != nil {
			if err := call.WP.PostWork("routine", call); err != nil {
				_log_info("ERROR: %s\n", err)
				time.Sleep(100 * time.Millisecond)
			}

		}
	default:
		log.Println("rpc: discarding Call reply due to insufficient Done chan capacity")
	}
}

func (call *Call) DoWork(workRoutine int) {

	call.Callback(call.Param, call.Reply, call.Error)
}

var ErrShutdown = errors.New("connection is shut down")

type Client struct {
	remoteAddr    string
	reqMutex      sync.Mutex // protects following
	mutex         sync.Mutex // protects following
	rwc           io.ReadWriteCloser
	seq           uint64
	pending       map[uint64]*Call //key is seq
	closing       bool             // user has called Close
	shutdown      bool             // server has told us to stop
	receivedCount uint64
	lastGap       uint64
	timeout       int
	consumer      *workpool.WorkPool
}

func (client *Client) reconnect() {

	for {

		client.mutex.Lock()
		if client.closing {
			client.mutex.Unlock()
			break
		}
		client.mutex.Unlock()

		var d net.Dialer
		d.KeepAlive = -1
		conn, err := d.DialContext(context.Background(), "tcp", client.remoteAddr)

		//conn, err := net.DialTCP("tcp", nil,  &net.TCPAddr{"172.30.46.80", 8097, " " })
		//conn, err := net.Dial("tcp", client.remoteAddr)
		if err == nil {

			//set read and write not timeout
			t := time.Time{}
			if err := conn.SetReadDeadline(t); err == nil {

				if err := conn.SetWriteDeadline(t); err == nil {
					client.mutex.Lock()
					client.rwc.Close()
					client.rwc = conn
					client.timeout = 0
					client.lastGap = 0
					client.shutdown = false
					client.pending = make(map[uint64]*Call)
					client.receivedCount = 0
					client.seq = 0
					client.mutex.Unlock()
					break

				}

			}

		}

		time.Sleep(time.Second)

	}

}

func (client *Client) getPackLength() (int, error) {

	var err error
	headLength := 0
	head := make([]byte, 8)
	for err == nil {
		var n int
		n, err = client.rwc.Read(head[headLength:])
		if err != nil {
			break
		}
		headLength = headLength + n

		if headLength == 8 {
			break
		}
	}
	if err != nil {
		return -1, err
	}

	dataLengthBuff := bytes.NewBuffer(head[:])
	var totalLength uint64
	err = binary.Read(dataLengthBuff, binary.LittleEndian, &totalLength)
	if err != nil {
		return -1, err
	}

	return int(totalLength), nil
}

func (client *Client) getBody(totalLength int) ([]byte, error) {

	bodyLength := totalLength - 8 + 8 //if async tail has 8 byte not included in body length
	_log_debug("bodyLength: ", bodyLength)
	body := make([]byte, bodyLength)
	bodyIndex := 0
	var err error
	for err == nil {
		var n int
		n, err = client.rwc.Read(body[bodyIndex:])
		if err != nil {
			break
		}
		bodyIndex = bodyIndex + n
		if bodyIndex == bodyLength {
			break
		}
	}

	if err != nil {
		return nil, err
	}

	return body, nil

}

func (client *Client) getSession(body []byte) (uint64, error) {

	bodyLength := len(body)
	//reqSessionBuff := bytes.NewBuffer(body[bodyLength-8 : bodyLength-8])
	reqSessionBuff := bytes.NewBuffer(body[bodyLength-8:])
	var reqSession uint64
	err := binary.Read(reqSessionBuff, binary.LittleEndian, &reqSession)
	return reqSession, err
}

func (client *Client) input() {

	var err error
	for err == nil {

		var totalLength int
		totalLength, err = client.getPackLength()
		if err != nil {
			_log_info(err)
			break
		}

		var body []byte
		body, err = client.getBody(totalLength)

		if err != nil {
			break
		}

		var reqSession uint64
		reqSession, err = client.getSession(body)
		if err != nil {
			break
		}

		client.mutex.Lock()
		call := client.pending[reqSession]
		delete(client.pending, reqSession)
		client.receivedCount++
		client.mutex.Unlock()

		switch {
		case call == nil:
			// We've got no pending call. That usually means that
			// WriteRequest partially failed, and call was already
			// removed; response is a server telling us about an
			// error reading request body. We should still attempt
			// to read error body, but there's no one to give it to.

			err = errors.New("call is nil")

		default:
			err = Decode(call.Reply, body[:totalLength-8-8]) //remove session and
			//err = Decode(call.Reply, body[:totalLength-8])
			if err != nil {
				call.Error = errors.New("reading body " + err.Error())
			}
			call.done()
		}
	}

	// Terminate pending calls.
	client.reqMutex.Lock()
	client.mutex.Lock()
	client.shutdown = true
	closing := client.closing
	if err == io.EOF {
		if closing {
			err = ErrShutdown
		} else {
			err = io.ErrUnexpectedEOF
		}
	}
	for _, call := range client.pending {
		call.Error = err
		call.done()
	}

	client.mutex.Unlock()
	client.reqMutex.Unlock()
	_log_debug("reconnect server")
	client.reconnect()
	client.input()

}

func (client *Client) checkServerHealth() {

	for {

		client.mutex.Lock()
		if client.closing {
			client.mutex.Unlock()
			return
		}

		if client.lastGap == (client.seq-client.receivedCount) && client.lastGap != 0 {

			client.timeout++

			if client.timeout == 6 {

				for _, call := range client.pending {
					call.Error = errors.New("server not response time out")
					call.done()
				}

				client.shutdown = true
				client.mutex.Unlock()
				client.reconnect()
				continue

			}

		} else {

			client.lastGap = client.seq - client.receivedCount

			client.timeout = 0

		}

		client.mutex.Unlock()
		time.Sleep(time.Second * 10)

	}

}

var PingReqFnType uint32

func (client *Client) ping() {
	type PingReq struct {
		Functype uint32
		Reserve  uint64
	}
	//todo change to ping func id
	req := PingReq{PingReqFnType, 0}

	type PingReply struct {
		Functype FuncType
		Err      uint32
		Reserve  uint64
	}

	for {

		reply := PingReply{}

		if err := client.Call("ping", req, &reply); err != nil {
			_log_info(err.Error())
		}

		time.Sleep(time.Second * 2)
	}
}

func (client *Client) Call(serviceMethod string, req interface{}, reply interface{}) error {

	call := <-client.Go(serviceMethod, req, reply, make(chan *Call, 1), nil, nil).Done
	return call.Error
}

// Go invokes the function asynchronously. It returns the Call structure representing
// the invocation. The done channel will signal when the call is complete by returning
// the same Call object. If done is nil, Go will allocate a new channel.
// If non-nil, done must be buffered or Go will deliberately crash.
func (client *Client) Go(serviceMethod string, req interface{}, reply interface{}, done chan *Call, param interface{}, backFunc CallBackFunc) *Call {
	call := new(Call)
	call.ServiceMethod = serviceMethod
	call.Req = req
	call.Reply = reply
	call.Param = param
	call.Callback = backFunc
	call.WP = client.consumer
	if done == nil {
		done = make(chan *Call, 10) // buffered.
	} else {
		// If caller passes done != nil, it must arrange that
		// done has enough buffer for the number of simultaneous
		// RPCs that will be using that channel. If the channel
		// is totally unbuffered, it's best not to run at all.
		if cap(done) == 0 {
			log.Panic("rpc: done channel is unbuffered")
		}
	}
	call.Done = done
	client.send(call)
	return call
}

func (client *Client) encodeHeadAndReq(call *Call) (*bytes.Buffer, int, error) {

	codecSize, err := SizeStruct(call.Req)
	if codecSize == -1 {
		return nil, -1, err
	}

	buffer := new(bytes.Buffer)
	var totalSize uint64
	totalSize = uint64(codecSize) + 8
	//pre alloc improve performance
	buffer.Grow(int(totalSize))
	err = Encode(totalSize, buffer)
	if err != nil {
		return nil, codecSize, err
	}
	_log_debug("first encode size:", codecSize, "content:", buffer.Bytes())
	err = Encode(call.Req, buffer)
	if err != nil {
		return nil, codecSize, err
	}
	_log_debug("Second encode size:", codecSize, "content:", buffer.Bytes())
	return buffer, codecSize, nil
}

func (client *Client) send(call *Call) {

	buffer, size, err := client.encodeHeadAndReq(call)
	if err != nil {
		call.Error = err
		call.done()
		return
	}
	_log_debug("size:", size)
	client.reqMutex.Lock()
	defer client.reqMutex.Unlock()

	client.mutex.Lock()
	if client.shutdown || client.closing {
		client.mutex.Unlock()
		call.Error = ErrShutdown
		call.done()
		return
	}
	seq := client.seq
	err = Encode(seq, buffer)
	if err != nil {
		client.mutex.Unlock()
		call.Error = err
		call.done()
		return
	}
	client.seq++
	client.pending[seq] = call
	client.mutex.Unlock()

	// Encode and send the request.

	num, err := client.rwc.Write(buffer.Bytes())
	_log_debug(buffer.Bytes())
	_log_debug("num:", num)
	if err != nil || num != size+8+8 {
		_log_info("write err dealing")
		client.mutex.Lock()
		call = client.pending[seq]
		delete(client.pending, seq)
		client.mutex.Unlock()
		if call != nil {
			call.Error = err
			call.done()
		}
	}
}

func (client *Client) Close() error {

	client.mutex.Lock()
	if client.closing {
		client.mutex.Unlock()
		return ErrShutdown
	}
	client.closing = true
	client.mutex.Unlock()
	client.consumer.Shutdown("routine")
	return client.rwc.Close()
}

// Dial connects to an RPC server at the specified network address.
func Dial(address string) (*Client, error) {

	var d net.Dialer
	d.KeepAlive = -1
	conn, err := d.DialContext(context.Background(), "tcp", address)
	//conn, err := net.Dial("tcp", address)
	if err != nil {
		return nil, err
	}

	//if tc, ok := conn.(* net.TCPConn); ok{
	//	tc.SetKeepAlive(false)
	//	tc.SetReadDeadline(t)
	//	tc.SetWriteDeadline(t)
	//
	//}

	//set read and write not timeout
	t := time.Time{}
	if err := conn.SetReadDeadline(t); err != nil {
		return nil, err
	}

	if err := conn.SetWriteDeadline(t); err != nil {
		return nil, err
	}

	return NewClient(conn, address), nil
}

func DialWithTimeOut(address string) (*Client, error) {

	return nil, nil
}

func NewClient(conn io.ReadWriteCloser, address string) *Client {
	numCpu := runtime.NumCPU()
	runtime.GOMAXPROCS(numCpu)
	workPool := workpool.New(runtime.NumCPU(), 800)

	client := &Client{
		remoteAddr: address,
		rwc:        conn,
		pending:    make(map[uint64]*Call),
		consumer:   workPool,
	}
	go client.input()

	go client.ping()

	go client.checkServerHealth()

	return client
}

type FuncType uint32
