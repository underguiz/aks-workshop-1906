from flask import Flask

#app = Flask(__name__)

@app.route('/')
@app.route('/aks')
def hello():
   return "AKS Workshop!"

if __name__ == '__main__':
   app.run("0.0.0.0", 4449)