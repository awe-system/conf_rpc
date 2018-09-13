生成客户端方法：
    python generate_client.py example.xml > client.py

生成h方法：（名称改变则需要改变cpp中include）
	python generate_server_cpp.py example.xml > transfer_thread.cpp

生成cpp方法：
	python generate_server_cpp.py example.xml > transfer_thread.cpp

编译方法：g++ -std=c++11 -lboost_system transfer_thread.cpp 
          若需要main里面的单例执行，加-DTESTTRANSTER_THREAD 
