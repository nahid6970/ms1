from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
shared_text = ""

@app.route("/", methods=["GET", "POST"])
def index():
    global shared_text
    if request.method == "POST":
        # Update the shared text with the submitted data
        shared_text = request.form["text"]
        # Redirect to the home page using GET method (Post/Redirect/Get pattern)
        return redirect(url_for('index'))
    
    # Render the index.html with the current shared text
    return render_template("index.html", shared_text=shared_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
