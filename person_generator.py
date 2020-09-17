import json
import random


class Person:
    def __init__(self, person_attributes: dict):
        self.fname = person_attributes['fname']
        self.lname = person_attributes['lname']
        self.nickname = person_attributes['nickname']
        self.sex = person_attributes['sex']
        self.email = person_attributes['email']
        self.pw = person_attributes['pw']
        self.client_secret = ''
        self.client_id = ''

    def to_string(self):
        s = 'Person Info:\n'
        s += ' First Name: {}\n Last Name: {}\n Nickname: {}\n Sex: {}\n'.format(
            self.fname, self.lname, self.nickname, self.sex)
        return s


class PersonGenerator:
    def __init__(self, json_file_path: str = 'input_data/emails.json'):
        self.json_file_path = json_file_path
        self.person_data = self.retrieve_person_data()
        self.males = [Person(i) for i in self.person_data['males']]
        self.remaining_males = self.males.copy()
        self.females = [Person(i) for i in self.person_data['females']]
        self.remaining_females = self.females.copy()
        self.picked_male_count = 0
        self.picked_female_count = 0

    def retrieve_person_data(self):
        f = open(self.json_file_path)
        data = json.load(f)
        f.close()
        return data

    def reset_panel(self):
        self.remaining_males = self.males.copy()
        self.remaining_females = self.females.copy()
        self.picked_male_count = self.picked_female_count = 0

    def pick_male(self):
        # pick a male if a 10-sided dice gives a 5 or less, else pick a female
        return True if random.randint(0, 9) < 5 else False

    def get_random_person(self, male: bool):
        # if True, pick a male, else pick a female
        if male:
            key = random.randint(0, len(self.remaining_males) - 1)
            res = self.remaining_males[key]
            self.remaining_males.pop(key)
            self.picked_male_count += 1
            return res
        else:
            key = random.randint(0, len(self.remaining_females) - 1)
            res = self.remaining_females[key]
            self.remaining_females.pop(key)
            self.picked_female_count += 1
            return res

    def get_person(self):
        # if panel is already full, return an error
        if self.picked_male_count + self.picked_female_count == 5:
            raise RuntimeError('Cannot pick another person, panel is full')
            return None
        # if 2 males and 2 females (panel size = 4), pick a person randomly for the 5th and final
        elif self.picked_male_count + self.picked_female_count == 4:
            return self.get_random_person(self.pick_male())
        # if panel is full of males, pick a female
        elif self.picked_male_count == 2:
            return self.get_random_person(False)
        # if panel is full of females, pick a male
        elif self.picked_female_count == 2:
            return self.get_random_person(True)
        # otherwise pick someone randomly
        else:
            return self.get_random_person(self.pick_male())

        


# TEST SCRIPT FOR CHECKING BALANCED GENDER PANEL
#p = PersonGenerator()
# for n in range(0, 10):
#     print(' Panel Test No. {}'.format(n))
#     for i in range(1, 6):
#         print('person {}'.format(i))
#         print(p.get_person())
#         print(' m count {} , f count {}'.format(p.picked_male_count, p.picked_female_count))

#         print(' ')
#     print(' ')
#     print(' ')
#     p.reset_panel()