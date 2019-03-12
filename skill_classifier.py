import numpy as np
import pandas as pd
import heapq

from scipy.stats import entropy
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class SkillClassifier(object):
    def __init__(self):
        self.model = None
        self.output = None
        self.data = None
        self.features = None
        self.skillsets_mappings = {}

    def train(self, n_topics=45):
        """
        Trains the Skill Classifier on the given dataset through an initial read and process of the data.

        param n_topics: The number of topics we want to cluster the data into
        type n_topics: int
        """
        print('Started training')
        raw_data = self._read_data()
        print('Started processing data')
        self.data, self.features = self._process_data(raw_data)
        self.model, self.output = self._calc_lda(
            self.data, num_topics=n_topics)
        print('Finished training')
        return

    def classify(self, user_skills):
        """
        Given a list of user skills, outputs for each user a primary and secondary skillset

        param user_skills: A list where each entry is a list of a user's skills
        type user_skills: list[list]
        """
        if self.model is None:
            print('Need to train model first before classification')
            return
        if len(self.skillsets_mappings) == 0:
            print(
                'Please assign skillsets first using the assign_skills() function'
            )
            return
        if len(user_skills) == 0 or not isinstance(user_skills[0], list):
            print(
                'User skills takes in a list of lists where each list corresponds to a users skills'
            )
            return

        ret = []
        for user in user_skills:
            process_skills = [skill.lower() for skill in user]
            curr_user = []
            for feature in self.features.get_feature_names():
                if feature in process_skills:
                    curr_user.append(1)
                else:
                    curr_user.append(0)
            curr_user = normalize(np.matrix(curr_user), axis=1)
            transformed_user = self.model.transform(curr_user)
            heap = []
            for i in range(len(transformed_user[0])):
                heapq.heappush(heap, (transformed_user[0][i], i))
            primary, secondary = heapq.nlargest(2, heap)
            ret.append((self.skillsets_mappings[primary[1]],
                        self.skillsets_mappings[secondary[1]]))
        return ret

    def assign_skills(self):
        """
        Allows the user to manually assign the skills outputted from LDA
        into one of the given skillsets
        """
        if self.model is None:
            print('Need to train model first before classification')
            return
        print('Choose the skillset that best match the given words')
        curr_skill = 0
        num_to_skill = {
            '1': 'Managerial And Administrative',
            '2': 'Sales-Oriented',
            '3': 'Communications',
            '4': 'Financial',
            '5': 'Technical',
            '6': 'Artistic',
            '7': 'Specialized/Other'
        }
        df_skill_keywords = self.calc_top_k_keywords(k_words=10)
        for row in df_skill_keywords.iterrows():
            skillset = None
            print(row)
            print(
                'Enter the number corresponding to the skillset that best matches the words.'
            )
            print('(1) Managerial And Administrative')
            print('(2) Sales-Oriented')
            print('(3) Communications')
            print('(4) Financial')
            print('(5) Technical')
            print('(6) Artistic')
            print('(7) Specialized/Other)')
            while skillset not in ('1', '2', '3', '4', '5', '6', '7'):
                print(
                    'Please enter the number corresponding to the skillset that best matches the words.'
                )
                skillset = input()
            self.skillsets_mappings[curr_skill] = num_to_skill[skillset]
            curr_skill += 1
        print('Finished manual assignment')
        return

    def calc_score(self):
        """
        Calculates the score associated with the trained model
        """
        # higher the better
        if self._check_model():
            return self.model.score(self.data)
        return

    def calc_perplexity(self):
        """
        Calculates the perplexity associated with the trained model
        """
        # lower the better
        if self._check_model():
            return self.model.perplexity(self.data)
        return

    def calc_avg_kl_divergence(self):
        """
        Calculates the average Kullback–Leibler divergence (relative entropy)
        associated with the trained model
        """
        if self._check_model():
            diverge = 0
            count = 0
            for i in range(len(self.model.components_)):
                for j in range(i + 1, len(self.model.components_)):
                    count += 1
                    diverge += entropy(self.model.components_[i],
                                       self.model.components_[j])
            return diverge / count
        return

    def calc_lda_distribution(self):
        """
        Calculates the number of data points in the training set assigned to each topic
        """
        if self._check_model():
            # column names
            skillsets = ["Skill" + str(i) for i in range(self.model.n_topics)]
            # row names
            people = ["Person" + str(i) for i in range(len(self.output))]

            # create data frame relating people to each of the skillsets
            df_people_skills = pd.DataFrame(
                np.round(self.output, 2), columns=skillsets, index=people)

            # Get dominant skill for each person
            dominant_skill = np.argmax(df_people_skills.values, axis=1)
            df_people_skills['Dominant Skill'] = dominant_skill
            df_skill_distribution = df_people_skills[
                'Dominant Skill'].value_counts().reset_index(
                    name='skill counts')
            df_skill_distribution.columns = ['Skill Num', 'Num People']
            return df_skill_distribution
        return

    def calc_top_k_keywords(self, k_words=15):
        """
        Calculate the top k words associated with each topic in the trained model
        """
        if self._check_model():
            # Topic-Keyword Matrix
            df_skill_keywords = pd.DataFrame(self.model.components_)
            # Assign Column and Index
            df_skill_keywords.columns = self.features.get_feature_names()
            df_skill_keywords.index = [
                "Skill" + str(i) for i in range(self.model.n_topics)
            ]

            # Topic - Keywords Dataframe
            keywords = np.array(self.features.get_feature_names())
            topic_keywords = []
            for topic_weights in self.model.components_:
                # sort in descending order
                top_keyword_idx = (-topic_weights).argsort()[:k_words]
                topic_keywords.append(keywords.take(top_keyword_idx))

            df_skill_keywords = pd.DataFrame(topic_keywords)
            df_skill_keywords.columns = [
                'Word ' + str(i) for i in range(df_skill_keywords.shape[1])
            ]
            df_skill_keywords.index = [
                'Skill ' + str(i) for i in range(df_skill_keywords.shape[0])
            ]
            return df_skill_keywords
        return

    def _read_data(self, chunksize=320):
        """
        Reads in the dataset into a data frame by chunks. Assumes that the data set
        is located in the same directory as the file. Picks a random entry from a uniform
        distribution to add to the training set.
        """
        #approximately 31685708 entries
        df = pd.DataFrame()
        curr_chunk = 0

        try:
            data = pd.read_csv(
                'all_skills_sorted.tsv', sep='\t', chunksize=chunksize)
        except:
            print('Move the dataset to the current working directory')

        for chunk in data:
            rand_person = chunk.sample(n=1)
            df = pd.concat([df, rand_person])

            # log progress every 10000 entries
            curr_chunk += 1
            if curr_chunk % 10000 == 0:
                print(str(curr_chunk) + ' entries read in')

        df.columns = ['subclass', 'skills']
        # shuffle the rows in the data frame to prevent converging at a poor minimum
        df = df.sample(frac=1)
        return df

    def _process_data(self, df):
        """
        Processes the data frame for use in LDA analysis. Drops sparse entries in dataframe
        and creates normalized feature matrix.
        """
        corpus = []
        for skills in df['skills']:
            corpus.append(skills)
        vectorizer = CountVectorizer(
            tokenizer=lambda x: x.split(','),
            min_df=10)  #drop sparse entries < 10 in corpus
        data_vectorized = normalize(vectorizer.fit_transform(corpus))
        data_processed = data_vectorized.toarray(
        )  # convert sparse matrix to full
        return data_processed, vectorizer

    def _calc_lda(self, data_processed, num_topics=45, max_iter=500):
        """
        Runs LDA on a given number of topics. Returns the model and the data fitted by the
        LDA transformation
        """
        print('Starting topic modeling through LDA...')
        lda_model = LatentDirichletAllocation(
            n_topics=num_topics, max_iter=max_iter)
        lda_output = lda_model.fit_transform(data_processed)
        print(lda_model)
        print('Shape of people to skills matrix is: ')
        print(lda_output.shape)
        print('Shape of skills to words matrix is: ')
        print(lda_model.components_.shape)
        print('Finished topic modeling...')
        return lda_model, lda_output

    def _check_model(self):
        if self.model is None:
            print('Need to train model first before calculating stats')
            return False
        return True
