from pydantic import BaseModel

class Test(BaseModel):
    key1: str
    key2: str
    key3: str = "3"
    _key5: str = ""

    def test(self):
        print("_key5:" + self._key5)

if __name__ == "__main__":
    test = Test(key1='1', key2='2')
    test.test()
