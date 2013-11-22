__author__ = 'koolaid'

import sys
import json


def get_element_types():
    return {
        'PSToggleSwitchSpecifier': ToggleElement,
        'PSSliderSpecifier': SliderElement,
        'PSTitleValueSpecifier': TitleElement,
        'PSGroupSpecifier': GroupElement,
        'PSTextFieldSpecifier': TextFieldElement,
        'PSMultiValueSpecifier': MultiValueElement,
        'PSRadioGroupSpecifier': RadioGroupElement,
        'PSChildPaneSpecifier': ChildPaneElement,
    }


def print_indent_tag(tag, value, indent_level, outf):
    print_indent('<' + tag + '>' + str(value) + '</' + tag + '>', indent_level, outf)


def print_indent(content, indent_level, outf):
    s = ' ' * (indent_level * 4)
    outf.write(s + content + '\n')

#    print s + content


files_to_process = []


class Plist:
    def __init__(self, d):
        self.properties = d
        self.elements = []

        for item in d['PreferenceSpecifiers']:
            itemtype = item['Type']
            claz = get_element_types()[itemtype]
            new_elem = claz(item)
            self.elements.append(new_elem)


    def saveplist(self, outfilename):
        indent_level = 0
        outf = open(outfilename, 'w')

        print_indent('<?xml version="1.0" encoding="UTF-8"?>', indent_level, outf)
        print_indent(
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
            indent_level, outf)
        print_indent('<plist version="1.0">', indent_level, outf)

        print_indent('<dict>', indent_level, outf)

        print_indent_tag('key', 'StringsTable', indent_level + 1, outf)
        print_indent_tag('string', self.properties['StringsTable'], indent_level + 1, outf)

        print_indent_tag('key', 'PreferenceSpecifiers', indent_level + 1, outf)

        # print the lot
        print_indent('<array>', indent_level + 1, outf)

        for elem in self.elements:
            elem.save(indent_level + 2, outf)

        print_indent('</array>', indent_level + 1, outf)

        print_indent('</dict>', indent_level, outf)
        print_indent('</plist>', indent_level, outf)
        outf.close()


class Element(object):
    default_types = {
        'Type': 'string',
        'SupportedUserInterfaceIdioms': 'array',
    }

    def __init__(self, d):
        self.properties = d

    def get_types(self):
        a = {}
        a.update(self.default_types)
        a.update(self.custom_types)  # grab it from subclass
        return a

    def save(self, indent_level, outf):
        print_indent('<dict>', indent_level, outf)
        for propname, propvalue in self.properties.iteritems():
            tp = self.get_types()[propname]

            if tp == 'array':
                # fetch datatype and items
                print_indent_tag('key', propname, indent_level + 1, outf)
                print_indent('<array>', indent_level + 1, outf)
                datatype = propvalue['datatype']
                for item in propvalue['items']:
                    print_indent_tag(datatype, item, indent_level + 2, outf)
                print_indent('</array>', indent_level + 1, outf)
            elif tp == 'boolean':
                if propvalue:
                    out = '<true/>'
                else:
                    out = '<false/>'

                print_indent_tag('key', propname, indent_level + 1, outf)
                print_indent(out, indent_level + 1, outf)

            elif tp == 'any':
                # figure out what any is
                possibles = {
                    type(2): 'integer',
                    type(u''): 'string',
                    type(2.3): 'real',
                }

                typ = possibles[type(propvalue)]

                print_indent_tag('key', propname, indent_level + 1, outf)
                print_indent_tag(typ, propvalue, indent_level + 1, outf)
            else:
                # just normal props
                print_indent_tag('key', propname, indent_level + 1, outf)
                print_indent_tag(tp, propvalue, indent_level + 1, outf)

        print_indent('</dict>', indent_level, outf)


class ToggleElement(Element):
    custom_types = {
        'Title': 'string',
        'Key': 'string',
        'DefaultValue': 'any',
        'TrueValue': 'any',
        'FalseValue': 'any',
    }


class SliderElement(Element):
    custom_types = {
        'Key': 'string',
        'DefaultValue': 'real',
        'MinimumValue': 'real',
        'MaximumValue': 'real',
        'MinimumValueImage': 'string',
        'MaximumValueImage': 'string',
    }


class TitleElement(Element):
    custom_types = {
        'Title': 'string',
        'Key': 'string',
        'DefaultValue': 'string',
        'Values': 'array',
        'Titles': 'array',
    }


class TextFieldElement(Element):
    custom_types = {
        'Title': 'string',
        'Key': 'string',
        'DefaultValue': 'string',
        'IsSecure': 'boolean',
        'KeyboardType': 'string',
        'AutoCapitalizationType': 'string',
        'AutoCorrectionType': 'string',
    }


class MultiValueElement(Element):
    custom_types = {
        'Title': 'string',
        'Key': 'string',
        'DefaultValue': 'any',
        'Values': 'array',
        'Titles': 'array',
        'ShortTitles': 'array',
        'DisplaySortedByTitle': 'boolean',
    }


class RadioGroupElement(Element):
    custom_types = {
        'Title': 'string',
        'FooterText': 'string',
        'Key': 'string',
        'DefaultValue': 'any',
        'Values': 'array',
        'Titles': 'array',
        'DisplaySortedByTitle': 'boolean',
    }


class ChildPaneElement(Element):
    custom_types = {
        'Title': 'string',
        'File': 'string',
    }

    def save(self, indent_level, outf):
        # remember the name of the File
        child_pane_name = self.properties['File']
        files_to_process.append(child_pane_name)

        super(ChildPaneElement, self).save(indent_level, outf)


class GroupElement(Element):
    custom_types = {
        'Type': 'string',
        'Title': 'string',
        'FooterText': 'string',
    }

    def __init__(self, d):
        super(Element, self).__init__()
        self.properties = d

        self.elements = []
        for item in d['subitems']:
            itemtype = item['Type']
            claz = get_element_types()[itemtype]
            new_elem = claz(item)

            self.elements.append(new_elem)


    def save(self, indent_level, outf):
        # print own props, minus 'subitems'
        del self.properties['subitems']
        super(GroupElement, self).save(indent_level, outf)

        # print subitems
        for elem in self.elements:
            elem.save(indent_level + 1, outf)


def process_file(dir_name, file_name, dest_dir):
    print 'Bundlegen: ' + dir_name + file_name + '.json  -->> ' + dest_dir + file_name + '.plist'
    infile = open(dir_name + file_name + '.json')
    data = json.load(infile)
    infile.close()

    plist = Plist(data)

    out_file_name = dest_dir + file_name + '.plist'
    plist.saveplist(out_file_name)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'params:'
        print '   - dirname with jsons, eg. ~/jsondir/'
        print '   - root filename (without .json)'
        print '   - dirname to store .plists, eg. ~/code/projects/awesomeapp/Settings.bundle/'
        exit()

    d_name = sys.argv[1]
    root_filename = sys.argv[2]  # without the json
    dest_dir = sys.argv[3]

    files_to_process.append(root_filename)

    while len(files_to_process) > 0:
        f_name = files_to_process[0]

        process_file(d_name, f_name, dest_dir)

        files_to_process.remove(f_name)
