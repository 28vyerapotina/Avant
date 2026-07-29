import pandas as pd
import random
import numpy as np
import json
from sklearn.svm import SVC
from sklearn import preprocessing, metrics
from sklearn.preprocessing import OneHotEncoder


def _load_question_records(dataset_path):
    """
    Load a dataset file and return a flat list of question-record dicts,
    ready for pd.json_normalize().

    Handles two shapes:
      1. A flat list of question objects (e.g. english_dataset.json):
         [ {...question...}, {...question...}, ... ]
      2. A nested "test battery" shape (e.g. dataMath.json):
         { "math_tests": [
             { "name": ..., "module_1": [ {...question...}, ... ],
                             "module_2": [ {...question...}, ... ] },
             ... more tests ...
         ] }
         Every list-valued field nested inside each test entry (module_1,
         module_2, etc., whatever they're named) gets flattened together
         into one combined list of question records.
    """
    with open(dataset_path, 'r') as data_file:
        data = json.load(data_file)

    if isinstance(data, list):
        return data

    records = []
    if isinstance(data, dict):
        for top_level_value in data.values():
            if not isinstance(top_level_value, list):
                continue
            for test_entry in top_level_value:
                if not isinstance(test_entry, dict):
                    continue
                for field_value in test_entry.values():
                    if isinstance(field_value, list):
                        records.extend(field_value)

    return records


class Dataframe_Questions():
    def __init__(self, dataset_path='english_dataset.json'):
        records = _load_question_records(dataset_path)
        normalized_data = pd.json_normalize(records, sep='.')
        self.df = pd.DataFrame(normalized_data)

        # Some datasets (e.g. dataMath.json) use the literal string "null"
        # instead of real JSON null for empty fields (paragraph, visuals,
        # etc.). Replace it so _get()'s pd.isna() checks in the question
        # scene actually catch it, instead of printing the word "null".
        self.df = self.df.replace("null", "")

        # NOTE: dropna(axis='columns') was removed here. It drops an entire
        # column if ANY row in the dataset is missing that value -- which
        # silently wipes out columns like question.choices.C/D (empty for
        # 2-option questions), question.paragraph (empty when there's no
        # passage), or worst case question.correct_answer, making every
        # question unanswerable. The question scene already handles missing
        # cells per-row via pd.isna(), so no blanket column drop is needed.

        if 'id' in self.df.columns:
            self.df = self.df.drop(columns='id')

        self.probs_df = pd.DataFrame(columns=[
            'domain', 'difficulty', 'question.choices.A', 'question.choices.B',
            'question.choices.C', 'question.choices.D', 'question.question',
            'question.paragraph', 'question.explanation', 'question.correct_answer'
        ])
        self.y = []

    def question_batch(self, iterations, indices):
        for i in range(iterations):
            if indices == []:
                # Sample from the DataFrame's actual current labels, not
                # positional integers -- rows may have been dropped already,
                # so len(self.df) no longer lines up with valid label values.
                if self.df.empty:
                    break
                rand_idx = random.choice(self.df.index.tolist())
                self.probs_df = pd.concat(
                    [self.probs_df, self.df.loc[[rand_idx]]], ignore_index=True
                )
                self.df = self.df.drop(rand_idx)
            else:
                self.probs_df = pd.concat(
                    [self.probs_df, self.df.loc[[indices[i]]]], ignore_index=True
                )
                self.df = self.df.drop(indices[i])

    def update_y(self, y):
        for i in y:
            self.y.append(i)

    def train_and_rank_hardest(self, count):
        """
        Train an SVM on (domain, difficulty) -> correct/incorrect using
        every question answered so far, then rank the remaining question
        pool (self.df) by how confidently the model expects the user to
        get each one WRONG.

        Returns a list of index labels (valid for self.df / question_batch)
        for up to `count` of the hardest remaining questions.

        Falls back to random sampling if there isn't enough signal yet --
        SVC needs to see at least one example of each class (right AND
        wrong) to fit, which won't be true on the very first batch.
        """
        if self.df.empty:
            return []

        count = min(count, len(self.df))

        if len(self.y) != len(self.probs_df) or len(set(self.y)) < 2:
            return random.sample(self.df.index.tolist(), count)

        ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False).set_output(transform='pandas')
        X = ohe.fit_transform(self.probs_df[['domain', 'difficulty']])
        y = self.y

        svm_clf = SVC(kernel='rbf', gamma='scale', C=1)
        svm_clf.fit(X, y)

        # Reuse the SAME fitted encoder (transform, not fit_transform) so
        # the remaining pool is encoded with the exact same columns/categories.
        # Just wanted to add --- I tried to figure out how to code this method myself for the AI question generation, 
        # but the model adapted it and helped me in parts to make it better and flow with the rest. It helped us understand
        # how to return the rows with the highest probabiliy for the player to miss, which was the initial object. For this reason,
        # although the AI definitely helped and generated some of these parts, we fully understand what it produced, we just needed
        # to know how to do it.
        
        X_remaining = ohe.transform(self.df[['domain', 'difficulty']])
        scores = svm_clf.decision_function(X_remaining)

        # svm_clf.classes_ is sorted, so [0, 1] -> negative scores point
        # toward class 0 (incorrect). Lower score = more confidently "wrong".
        ranked = pd.Series(scores, index=self.df.index).sort_values()
        print("Return harder questions...")
        return ranked.index.tolist()[:count]