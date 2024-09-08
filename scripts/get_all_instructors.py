import json
from pprint import pprint
from pymongo import MongoClient

from peloton import PelotonHumanInstructor, PylotonZMV
from peloton.constants import INSTRUCTORS_DICT

# conn = PylotonZMV('asdf', 'asdf')
# data = conn.get_all_instructors()['data']
# print(len(data))

# instructor_list = [PelotonHumanInstructor(**instructor_data) for instructor_data in data]

# instructors_dict = {instructor.instructor_id: instructor.model_dump() for instructor in instructor_list}
# print(instructors_dict)

# client = MongoClient(host='portainarr.box', port=27017)
# db = client.peloton
# collection = db.peloton_instructors

# # collection.insert_many([instructor.model_dump() for instructor in instructor_list])


# # instructor_data = collection.find_one({'instructor_id': 'a8c56f162c964e9392568bc13828a3fb'})
# # instructor = PelotonHumanInstructor(**instructor_data)
# # print(instructor.full_name)

# all_instructor_data = collection.find_one('instructor_name_dict')

# # for instructor_data in all_instructor_data:
# #     print(instructor_data['full_name'])
#     # instructor = PelotonHumanInstructor(**instructor_data)
#     # print(instructor.full_name)

# # instructor_name_dict = {instructor_data['instructor_id']: instructor_data['full_name'] for instructor_data in all_instructor_data}
# # instructor_name_dict.update({'_id': 'instructor_name_dict'})
# # collection.insert_one(instructor_name_dict)
# pprint(all_instructor_data)

print(INSTRUCTORS_DICT.get('asdf', None))