import os
from flask import Flask
from app import create_app #실제 앱은 app/ 폴더 안에서 정의할예정정

app = create_app() #앱을 만들어주는 함수. 

if __name__ == '__main__':
    print("Base path:", os.getcwd())  # 현재 실행 경로 출력
    app.run(debug=True) #Flask 앱을 실행하는 코드. 
    #debug=True는 코드 바뀌면 자동 재시작되게 해줘서 개발편의성성
