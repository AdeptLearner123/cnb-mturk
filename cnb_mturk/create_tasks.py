from .create_task_xml import create_task_xml

from argparse import ArgumentParser
import random
import boto3
import os
import json

MTURK_SANDBOX = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
MTURK_KEY = os.getenv("MTURK_KEY")
MTURK_SECRET_KEY = os.getenv("MTURK_SECRET_KEY")

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-n", "--num-tasks", type=int, required=True)
    parser.add_argument("-p", "--pairs-per-task", type=int, required=True)
    args = parser.parse_args()
    return args.num_tasks, args.pairs_per_task


def get_words():
    with open("cardwords.txt", "r") as file:
        words = file.read().splitlines()
    return words


def main():
    num_tasks, pairs_per_task = parse_args()
    words = get_words()

    mturk = boto3.client('mturk',
        aws_access_key_id = MTURK_KEY,
        aws_secret_access_key = MTURK_SECRET_KEY,
        region_name='us-east-1',
        endpoint_url = MTURK_SANDBOX
    )

    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my account")

    for i in range(num_tasks):
        pairs = [ random.sample(words, 2) for j in range(pairs_per_task)]
        HIT_id = create_task(mturk, pairs)

        pairs_json = [ { "word1": word1, "word2": word2 } for word1, word2 in pairs ]

        with open(os.path.join("tasks", f"{HIT_id}.json"), "w+") as file:
            file.write(json.dumps({
                "HIT_id": HIT_id,
                "pairs":pairs_json
            }, indent=4))


def create_task(mturk, pairs):
    xml = create_task_xml(pairs)
    new_hit = mturk.create_hit(
        Title = f"Give a Code Names clue and explanations for the following {len(pairs)} pair of words.",
        Description = "For each of the word pairs, give a single-word Code Names clue that is related to both of the words in the pair.",
        Keywords = "text",
        Reward = "1.00",
        MaxAssignments = 1,
        LifetimeInSeconds = 172800,
        AssignmentDurationInSeconds = 7200,
        AutoApprovalDelayInSeconds = 14400,
        Question = xml,
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
    return new_hit['HIT']['HITId']


if __name__ == "__main__":
    main()