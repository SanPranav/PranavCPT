from flask import Flask, render_template, request, Response
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handle POST request to generate study plan
    if request.method == 'POST':
        try:
            # Extract form data
            test_date = request.form['testDate']
            subjects = [s.strip() for s in request.form['subjects'].split(',') if s.strip()]
            daily_hours = int(request.form['dailyHours'])
            difficulty = [request.form[f'difficulty_{s.lower()}'] for s in subjects]
            priority = [int(request.form[f'priority_{s.lower()}']) for s in subjects]
            
            # Calculate days until the test
            days_until_test = max(1, (datetime.strptime(test_date, '%Y-%m-%d') - datetime.now()).days)

            # Generate study plan and calculate efficiency score
            study_plan = generate_study_plan(subjects, daily_hours, difficulty, priority, days_until_test)
            efficiency_score = calculate_efficiency_score(study_plan, difficulty, priority)

            # Render the template with the generated data
            return render_template('index.html', study_plan=study_plan, efficiency_score=efficiency_score, days_until_test=days_until_test)
        except Exception as e:
            # Handle errors and render the template with an error message
            return render_template('index.html', error=f"An error occurred: {str(e)}", study_plan=None, efficiency_score=None)

    # Render the template for GET requests
    return render_template('index.html', study_plan=None, efficiency_score=None)

@app.route('/download', methods=['POST'])
def download():
    try:
        # Extract form data
        test_date = request.form['testDate']
        subjects = [s.strip() for s in request.form['subjects'].split(',') if s.strip()]
        daily_hours = int(request.form['dailyHours'])
        difficulty = [request.form[f'difficulty_{s.lower()}'] for s in subjects]
        priority = [int(request.form[f'priority_{s.lower()}']) for s in subjects]
        
        # Calculate days until the test
        days_until_test = max(1, (datetime.strptime(test_date, '%Y-%m-%d') - datetime.now()).days)

        # Generate study plan
        study_plan = generate_study_plan(subjects, daily_hours, difficulty, priority, days_until_test)

        # Prepare the study plan as a formatted text file
        output = f"Study Plan (Test Date: {test_date})\n"
        output += "=" * 40 + "\n"
        for subject, details in study_plan.items():
            output += f"Subject: {subject}\n"
            output += f"  Hours per Day: {details['hours_per_day']}\n"
            output += f"  Total Hours: {details['total_hours']}\n"
            output += f"  Sessions per Day: {details['sessions_per_day']}\n"
            output += f"  Difficulty: {details['difficulty']}\n"
            output += f"  Priority: {details['priority']}\n"
            output += "-" * 40 + "\n"

        # Create a response to download the file
        return Response(
            output,
            mimetype="text/plain",
            headers={"Content-Disposition": "attachment;filename=study_plan.txt"}
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"

def generate_study_plan(subjects, daily_hours, difficulty, priority, days):
    # Initialize the study plan dictionary
    plan = {}
    # Calculate the total weight based on priorities
    total_weight = sum(priority) or len(subjects)

    for i, subject in enumerate(subjects):
        # Adjust weight based on difficulty level
        diff_factor = {'easy': 0.8, 'hard': 1.2}.get(difficulty[i].lower(), 1.0)
        weight = priority[i] / total_weight
        # Calculate total hours for the subject
        total_hours = daily_hours * days * weight * diff_factor

        # Populate the study plan for the subject
        plan[subject] = {
            'hours_per_day': round(total_hours / days, 1),
            'total_hours': round(total_hours, 1),
            'sessions_per_day': max(1, int((total_hours / days) * 2)),
            'difficulty': difficulty[i].lower(),
            'priority': priority[i]
        }
    return plan

def calculate_efficiency_score(study_plan, difficulty, priority):
    # Initialize the efficiency score
    score = 0
    for i, subject in enumerate(study_plan):
        # Calculate priority score and difficulty bonus
        priority_score = priority[i] * 10
        diff_bonus = 20 if difficulty[i].lower() == 'hard' and study_plan[subject]['hours_per_day'] >= 2 else 10
        score += priority_score + diff_bonus

    # Return the normalized efficiency score (max 100)
    return min(100, score / len(study_plan))

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)
