from fastchat.serve.inference import Inferencer

if __name__ == "__main__":
    inferencer = Inferencer()
    inferencer.init("/home/luguanglong/Models/public/vicuna_v2/vicuna-7b")
    inferencer.execute("write a function in c++, sum 1+2")
