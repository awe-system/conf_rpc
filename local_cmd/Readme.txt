���ɿͻ��˷�����
    python generate_client.py example.xml > client.py

����h�����������Ƹı�����Ҫ�ı�cpp��include��
	python generate_server_cpp.py example.xml > transfer_thread.cpp

����cpp������
	python generate_server_cpp.py example.xml > transfer_thread.cpp

���뷽����g++ -std=c++11 -lboost_system transfer_thread.cpp 
          ����Ҫmain����ĵ���ִ�У���-DTESTTRANSTER_THREAD 
