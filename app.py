from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("mainscreen/index.html")


@app.route('/alltasks')
def alltasks():
    return render_template('mainscreen/alltasks.html')


@app.route('/history')
def history():
    return render_template('mainscreen/history.html')

if __name__ == '__main__':
    app.run(debug=True)