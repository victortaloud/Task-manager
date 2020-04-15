import requests
import re
import clipboard
import datetime as dt
import inspect

class Weekplan :
    def __init__(self):
        self.s = requests.Session()
        self.header = {'content-type': 'application/json', 'referer': 'http://api.weekplan.net'}
        self.para = {'EmailAddress': 'victor.taloud@artefact.com',
        'Password': '', # TODO add password
        'Timezone': 180}
        self.task = clipboard.get() 
        self.parameters_users, self.cookies_to_stay_connected = self.make_connexion(session_=self.s, params_=self.para, headers_ = self.header)
        self.start_url = 'http://api.weekplan.net/'
    def get_infos_connexion(self):
        return self.make_connexion(session_=self.s, params_=self.para, headers_ = self.header)
    
    def add_tasks_from_text(self) :
        texttaskwithoutdesc = ''.join([(val.split('}}')[0] \
                                        if len(val.split('}}')) ==1 \
                                        else val.split('}}')[1]) \
                                       for val in self.task.split('{{')])
        task_to_add_without_description = self.delete_useless_returntoline_in_task_without_description(
            texttaskwithoutdesc.split('-')[1:]
        )
        task_to_add_with_description = self.treat_when_comma_in_description(self.task)
        
        print(task_to_add_with_description)
        print('/n --- Tasks ----------/n {}'.format(task_to_add_without_description))
        for task in task_to_add_without_description :
            #print('-----\n - Task: {}\n-----\n  '.format([task]))
            data = {
                      "Text": task.split(':')[0],
                      "UserId": self.parameters_users['UserId'],
                      "WorkspaceId": self.parameters_users['WorkspaceId'],
                      'Date' : str(dt.datetime.today()),
                      'Notes' :''.join([ '' if len(task.split(':')) ==1 \
                                        else task.split(':')[1],self.get_description_of_the_task(
                                            task,task_to_add_with_description
                                        )]),
                      'TimeEstimated':None if len(task.split('#')) < 2 else task.split('#')[1][0], #v2
                      'TimeEstimatedType':2 #v2
                    }
            #print('-- Notes --------\n'+data['Notes'])
            rep = requests.post(self.start_url+'v2/actions', cookies=self.cookies_to_stay_connected, json=data)
    
    @staticmethod
    def make_connexion(session_, params_, headers_ ):
        rep = session_.post('http://api.weekplan.net/v2/sessions', json=params_, headers=headers_)
        param_id = rep.json()
        jar = requests.cookies.RequestsCookieJar()
        jar.set('.ASPXAUTH2' ,rep.cookies['.ASPXAUTH2'])
        return param_id, jar
    
    @staticmethod
    def get_description_of_the_task(task_, listtaskswithdescriptions_):  
        taskwithdescription = ''.join([valop for valop in listtaskswithdescriptions_ if task_.replace('  ','') in valop])
        return '' if '{{' not in taskwithdescription else taskwithdescription.split('{{')[1].split('}}')[0]
    
    @staticmethod 
    def treat_when_comma_in_description(tasks_with_description_and_comma_problem_):
        
        def add_comma_back_in_the_description(task_to_concat_) : 
            #add_commaback_in_the_description
            task_to_concat_with_comma = []
            for i,taski in enumerate(task_to_concat_) : 
                if len(task_to_concat_) > 0 and i == 1 : 
                    task_to_concat_with_comma.append('-'+taski)  
                else : 
                    task_to_concat_with_comma.append(taski)
            return task_to_concat_with_comma
        
        list_task_with_description = tasks_with_description_and_comma_problem_.split('-')[1:]
        list_right_tasks = [task for task in \
                            list_task_with_description \
                            if ('{{' in task and '}}' in task) or ('{{' not in task and '}}' not in task)]
        list_right_tasks = list_right_tasks if len(list_right_tasks) > 0 else []        
        task_to_concat = [task for task in list_task_with_description if task not in list_right_tasks]
        task_with_description_concat = ''.join(add_comma_back_in_the_description(task_to_concat))
        return list_right_tasks+[task_with_description_concat]
    
    @staticmethod
    def delete_useless_returntoline_in_task_without_description(list_of_task_with_return_to_line_): 
        list_of_task_treated = []
        #print(list_of_task_with_return_to_line_)
        for task_with_return_to_line in list_of_task_with_return_to_line_ : 
            while task_with_return_to_line.endswith(' ') : 
                task_with_return_to_line = task_with_return_to_line[:-1]
            while task_with_return_to_line.endswith('\n') : 
                task_with_return_to_line = task_with_return_to_line[:-2]
            while task_with_return_to_line.endswith(' ') : 
                task_with_return_to_line = task_with_return_to_line[:-1]
            list_of_task_treated.append(task_with_return_to_line)
        #print(list_of_task_treated)
        return list_of_task_treated
        
        
#print("====================\n====================\n====================")  
Weekplan().add_tasks_from_text()
