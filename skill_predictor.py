import kenlm
import numpy as np

import os
import heapq
import json
import collections
import random
import datetime
import itertools


class SkillPredictor(object):
    def __init__(self):
        self.data = []

        # make sure skills.json is in CWD
        with open('skills.json') as f:
            for line in f:
                self.data.append(json.loads(line))

        # dict mapping each user to the skills it has at each particular time stamp
        self.user_skills = {}  # str -> int -> str
        self.all_skills = set()
        for user in self.data:
            curr_user_skills = collections.defaultdict(set)
            curr_skills = set()
            curr_time = user['skills'][0]['src']['at']
            for s in user['skills']:
                time_stamp = s['src']['at']
                curr_skill = s['val']
                curr_skill = curr_skill.replace(" ", "")
                curr_skill = curr_skill.lower()
                curr_user_skills[time_stamp].add(curr_skill)
                self.all_skills.add(curr_skill)
            self.user_skills[user['id']] = curr_user_skills

        self.mle_bagsize = {}
        self.skill_acquisition_times = None
        self.model = None

    def get_bag_size_statistics(self):
        """
        Finds the average bag size and number of bags for a dataset.
        """
        avg_bag_size = 0
        num_bags = 0
        for user, bags in self.user_skills.items():
            if len(bags) <= 1:
                continue
            for bag in bags.values():
                if len(bag) > 2:
                    avg_bag_size += len(bag)
                    num_bags += 1
        return 'Average bag size: ' + str(avg_bag_size / num_bags) + '; Number bags: ' + str(num_bags)

    def _generate_skill_acquisition_times(self):
        self.skill_acquisition_times = collections.defaultdict(list)
        for user, time_stamps in self.user_skills.items():
            entries = list(time_stamps.keys())
            if len(entries) <= 1:
                continue
            for i in range(1, len(entries)):
                curr_skills = time_stamps[entries[i]]
                prev_skills = time_stamps[entries[i-1]]
                curr_day = datetime.datetime.fromtimestamp(entries[i] / 1000)
                prev_day = datetime.datetime.fromtimestamp(entries[i-1] / 1000)
                day_diff = (curr_day - prev_day).total_seconds() / \
                    (60 * 60 * 24)
                for skill in curr_skills:
                    if skill not in prev_skills:
                        for prev_skill in prev_skills:
                            self.skill_acquisition_times[(
                                prev_skill, skill)].append(day_diff)

            # for transitions with multiple records, take avg
            for transition, time in self.skill_acquisition_times.items():
                if len(time) > 1:
                    self.skill_acquisition_times[transition] = [
                        sum(time) / len(time)]

    def get_skill_acquisition_times(self, skill1, skill2):
        """
        Finds the average acquisition time for a given skill transition
        """
        if self.skill_acquisition_times is None:
            self._generate_skill_acquisition_times()
        entry = (skill1, skill2)
        if entry not in self.skill_acquisition_times:
            print('No previous record of this acquisition')
            return
        return str(round(self.skill_acquisition_times[entry][0], 3)) + ' days'

    def generate_data(self, num_permutations=1000):
        """
        Generates the data necessary for KenLM. Attempts to look over skill additions and deletions in a dataset and generates such changes as sentences
        """
        log = 0
        # remove previous instances of files
        try:
            os.remove('train_data.txt')
            os.remove('test_data.txt')
        except OSError as e:
            pass

        for user, time_stamps in self.user_skills.items():
            # starting data generation
            if log % 1000 == 0:
                print(str(log) + ' entries completed out of ' +
                      str(len(self.user_skills)))
            log += 1
            entries = list(time_stamps.keys())
            if len(entries) <= 1:
                continue
            for i in range(1, len(entries)):
                curr_skills = time_stamps[entries[i]]
                prev_skills = time_stamps[entries[i-1]]
                if len(prev_skills) <= 2:
                    continue

                # bag transition size
                if len(curr_skills) != len(prev_skills):
                    if len(prev_skills) not in self.mle_bagsize:
                        self.mle_bagsize[len(prev_skills)
                                         ] = collections.defaultdict(int)
                    self.mle_bagsize[len(prev_skills)][len(curr_skills)] += 1

                # skill additions
                for skill in curr_skills:
                    if skill not in prev_skills:
                        with open('train_data.txt', 'a') as f, open('test_data.txt', 'a') as g:
                            counter = 0
                            tmp_prev_skills = itertools.permutations(
                                list(prev_skills))
                            for permutation in tmp_prev_skills:
                                curr_sentence = list(permutation) + [skill]
                                curr_sentence = ' '.join(curr_sentence)
                                if np.random.rand() < 0.8:
                                    f.write('%s\n' % curr_sentence)
                                else:
                                    g.write('%s\n' % curr_sentence)
                                counter += 1
                                if counter > num_permutations:
                                    break

                # skill deletions
                for skill in prev_skills:
                    if skill not in curr_skills:
                        with open('train_data.txt', 'a') as f, open('test_data.txt', 'a') as g:
                            counter = 0
                            tmp_prev_skills = itertools.permutations(
                                list(prev_skills))
                            for permutation in tmp_prev_skills:
                                curr_sentence = list(
                                    permutation) + ['-' + skill]
                                curr_sentence = ' '.join(curr_sentence)
                                if np.random.rand() < 0.8:
                                    f.write('%s\n' % curr_sentence)
                                else:
                                    g.write('%s\n' % curr_sentence)
                                counter += 1
                                if counter > num_permutations:
                                    break

    def train(self):
        """
        Trains the given KenLM model on a language model dataset
        """
        try:
            self.model = kenlm.Model('../kenlm/build/train_data.arpa')
        except:
            print('Data file not found')
            print(
                'Run generate_data() and move the train_data.txt to ../kenlm/build/ folder')
            print('In ../kenlm/build/ folder run the following command in Terminal: bin/lmplz -o 6 < train_data.txt > train_data.arpa --discount_fallback')
            print('Try again')

    def predict(self, sentence):
        """
        Predicts the next bag of skills given a current bag of skills as a sentence
        """
        if self.model is None:
            print('Run train() first to train the model')
            return
        heap = []
        next_bag = []

        # add deletion skills
        prediction_skills = list(self.all_skills)[:]
        negation_skills = ['-' + skill for skill in self.all_skills]
        prediction_skills.extend(negation_skills)

        skills_list = sentence.split()
        prev_bag_len = len(skills_list)
        if prev_bag_len in self.mle_bagsize:
            counter = max(
                self.mle_bagsize[prev_bag_len], key=self.mle_bagsize[prev_bag_len].get)
        else:
            counter = prev_bag_len

        for skill in prediction_skills:
            curr_sentence = sentence + ' ' + skill
            curr_score = self.model.score(curr_sentence, bos=True, eos=True)
            heapq.heappush(heap, (-curr_score, skill))
        while counter > 0:
            _, next_skill = heapq.heappop(heap)
            if next_skill[0] != '-':
                next_bag.append(next_skill)
                counter -= 1
        return next_bag
