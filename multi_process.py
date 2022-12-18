from multiprocessing import Process, Queue
import face_detect as fd
from Yolo_lying.yolov5 import detect as y
cam1,cam2=1,2

if __name__ == "__main__":
    result = Queue()
    th1 = Process(target=fd.find_wanted,args=(cam1))
    th2 = Process(target=y.run, args=('./yolov5/lying_1216_l.pt',cam2))

    th1.start()
    th2.start()
    th1.join()
    th2.join()