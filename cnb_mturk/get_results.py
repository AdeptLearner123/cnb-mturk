import boto3
import os
import json
import xmltodict

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
MTURK_KEY = os.getenv("MTURK_KEY")
MTURK_SECRET_KEY = os.getenv("MTURK_SECRET_KEY")

def main():
    mturk = boto3.client('mturk',
        aws_access_key_id = MTURK_KEY,
        aws_secret_access_key = MTURK_SECRET_KEY,
        region_name='us-east-1',
        endpoint_url = MTURK_SANDBOX
    )

    tasks = []
    for filename in os.listdir("tasks/"):
        file_path = os.path.join("tasks", filename)
        with open(file_path, "r") as file:
            data = json.loads(file.read())
            tasks.append((file_path, data))
    
    print("Total tasks", len(tasks))
    tasks_without_results = [ (path, task) for path, task in tasks if "result" not in tasks ]
    print("Tasks missing results", len(tasks_without_results))

    for path, task in tasks_without_results:
        get_results(mturk, task)
        with open(path, "w") as file:
            file.write(json.dumps(task, indent=4))


def get_results(mturk, task):
    HIT_id = task["HIT_id"]
    # We are only publishing this task to one Worker
    # So we will get back an array with one item if it has been completed
    worker_results = mturk.list_assignments_for_hit(HITId=HIT_id, AssignmentStatuses=['Submitted'])

    if worker_results['NumResults'] > 0:
        assignment = worker_results["Assignments"][0]
        xml_doc = xmltodict.parse(assignment["Answer"])
        
        answers = xml_doc["QuestionFormAnswers"]["Answer"]
        answers_dict = { answer["QuestionIdentifier"]: answer["FreeText"] for answer in answers }
        print("Received answers:", answers_dict)

        for i in range(len(task["pairs"])):
            clue = answers_dict[f"pair_{i}_clue"]
            explanation1 = answers_dict[f"pair_{i}_explanation1"]
            explanation2 = answers_dict[f"pair_{i}_explanation2"]

            task["pairs"][i]["result"] = {
                "clue": clue,
                "explanation1": explanation1,
                "explanation2": explanation2
            }
    else:
        print("No results ready yet")
        return None


if __name__ == "__main__":
    main()