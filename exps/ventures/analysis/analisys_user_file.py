from os import *
import pandas as pd
import analysis_helper


class User(object):
    """
    Object of this class contains information about one user files.
    Especially, it extracts one path to needed files.
    After arranging data in neat folders, it is no longer as important.
    """

    def __init__(self, name):
        self.name = name.upper()
        print("*** ", self.name, " ***")
        self.complete = False
        self.session_type = self.get_session_type()
        self.all_files_list = self.get_files()
        self.all_files_list = self.remove_duplicate(self.all_files_list)
        self.pretest_files_list = self.one_type_files("pretest", "dual")
        self.postest_files_list = self.one_type_files("post", "dual")
        self.pretest = self.get_proper(self.pretest_files_list)
        self.postest = self.get_proper(self.postest_files_list)
        if self.pretest is not None and self.postest is not None:
            self.complete = True
        self.pretest = self.cut_extension(self.pretest)
        self.postest = self.cut_extension(self.postest)
        if self.pretest is not None and self.postest is not None:
            self.pre_post_file = File(self.find_file(self.pretest),
                                      self.find_file(self.postest), self)
        else:
            self.pre_post_file = None

    def get_session_type(self):
        """
        Checks in users.csv (in folder named 'data', provide a proper path!)
        which type of session this user was performing.
        """
        data = pd.read_csv('users.csv', index_col=0, dtype='str')
        if self.name in data['ID'].values:
            return data[data['ID']==self.name]['session_type'].values[0]
        else:
            return None

    def get_files(self):
        """
        Gets data files from a folder 'pre_post_data' (data was arranged there
        as: pre_post_data/username/pre_or_post/files_of_user
        """
        list = []
        for paths, subcatalogs, files in walk(r'./pre_post_data'):
            for file in files:
                if self._compare_name(file) and 'resampled' in file:
                    list.append(file)
        return list

    def _compare_name(self, file):
        """
        Checks if a file concerns the object.
        """
        name_str = str(self.name)
        file_str = str(file)
        if name_str in file_str:
            return True
        else:
            return False

    def remove_duplicate(self, mylist):
        """
        Removes duplicates from list
        """
        if not mylist:
            return None
        mylist = set(mylist)
        return list(mylist)

    def one_type_files(self, substring, notsubstring="tegonapewnoniema"):
        """
        Returns a list of strings containing those which have substring
        and don't have 'notsubstring'.
        """
        list = []
        for file in self.all_files_list:
            string = str(file)
            if (substring in string) and (notsubstring not in string):
                list.append(file)
        return list

    def get_proper(self, list):
        """
        Provisional function which tries to find the proper filename from
        very messy data.
        """
        youngest = 0
        thisfile = ""
        for file in list:
            date_in_string = analysis_helper.get_date_from_path(file)
            current = analysis_helper.date_to_int(date_in_string)
            if current > youngest:
                filename = self.cut_extension(file)
                countfiles = 0
                for filee in self.all_files_list:
                    if filename.lower() in filee.lower():
                        countfiles += 1
                if countfiles > 2:
                    youngest = current
                    thisfile = file
        if thisfile == "":
            return None
        else:
            return thisfile

    def get_dual(self, set, param):
        """
        Similar to function above, but concerning the 'dual' files.
        """
        if set is None:
            return None
        if len(set) > 2:
            return "More than 2 files."
        if len(set) == 1:
            if param == "older":
                return set.pop()
            return None
        list = []
        for elem in set:
            list.append(elem)
        first_elem_date_str = \
            analysis_helper.date_to_int(analysis_helper.get_date_from_path(list[0]))
        second_elem_date_str = \
            analysis_helper.date_to_int(analysis_helper.get_date_from_path(list[1]))
        if first_elem_date_str > second_elem_date_str:
            youngest = list[0]
            oldest = list[1]
        else:
            youngest = list[1]
            oldest = list[0]
        if param == "older":
            return oldest
        elif param == "younger":
            return youngest
        else:
            return "Invalid param."

    def cut_extension(self, file):
        """
        Removes extension from filename.
        """
        if file is None:
            return None
        string = ""
        for char in file:
            if char == '.':
                return string
            else:
                string += char

    def find_file(self, name):
        """
        Finds a full path to file from messy data, having only a filename.
        """
        if name is None:
            return None
        for paths, subcatalogs, files in walk(r'.'):
            for file in files:
                if name.lower() in file.lower():
                    return path.join(paths, file)
        return "There is no such file"

class File(object):
    """
    Extracts parameters from one file.
    """

    def __init__(self, path_pre, path_post, users):
        self.user = users
        self.path_pre = self.cut_extension(path_pre)
        self.path_post = self.cut_extension(path_post)
        self.obci_w_pre = analysis_helper.get_read_manager(self.path_pre)
        self.obci_w_post = analysis_helper.get_read_manager(self.path_post)
        if self.obci_w_pre and self.obci_w_post:
            self.obci_markers = get_markers(self.obci_w_pre, self.obci_w_post,
                                            self.user.name, self.user.session_type)
            self.romberg = get_romberg(self.obci_w_pre, self.obci_w_post,
                                       self.user.name, self.user.session_type)
        else:
            self.obci_markers = None
            self.romberg = None

    def cut_extension(self, file):
        if file is None:
            return None
        return ".".join(file.split('.')[:-2])
