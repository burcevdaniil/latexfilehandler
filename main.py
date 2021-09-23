import tkinter.filedialog
from PIL import ImageTk
import threading
from tkinter import *
from tkinter import ttk
from pylatexenc.latexwalker import LatexGroupNode, LatexMacroNode
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMathNode, LatexCharsNode
from pylatexenc.latex2text import LatexNodes2Text, MacroTextSpec, EnvironmentTextSpec, SpecialsTextSpec
from pylatexenc import latex2text, latexwalker, macrospec
from pylatexenc.macrospec import LatexContextDb, ParsedMacroArgs, MacroStandardArgsParser, MacroSpec, EnvironmentSpec, \
    SpecialsSpec
import re
import io
import time
import tkinter.messagebox as mb

root = Tk()
author = []
page = []
tex_dir = []
tex_path = []
dir_main = []
threads_num = [0]
lang_type = []
tex_cls = []
thebibliography_pos_check = [0, 0, 'temp']
check_article = [False]

text_format = {
    'author': [],
    'udk': [],
    'msc': [],
    'abstract': [],
    'keywords': [],
    'title': [],
    'thebibliography': [],
    'avtore': [],
    'abstracte': [],
    'keywordse': [],
    'naze': [],
    'author_info': [],
    'doi': [],
    'bibliographyl': []
}

ru_str_journal_title = ' Известия Иркутского государственного университета. Серия Математика. '
eng_str_journal_title = '<i>The Bulletin of Irkutsk State University. Series Mathematics. </i>'
eng_literals = ['Author(s)\n', 'Abstract\n', 'About the authors\n', 'For citation\n', eng_str_journal_title, ', Vol. ',
                ', pp. ', 'Keywords\n', 'UDC\n', 'MSC\n', 'DOI\n', 'References\n', '. ']
ru_literals = ['Автор(ы)\n', 'Аннотация\n', 'Об авторах\n', 'Ссылка для цитирования\n', ru_str_journal_title, '. Т. ',
               '. С. ', 'Ключевые слова\n', 'УДК\n', 'MSC\n', 'DOI\n', 'Литература\n', ' // ']


def clear_text_format():
    text_format['author'].clear()
    text_format['udk'].clear()
    text_format['msc'].clear()
    text_format['abstract'].clear()
    text_format['keywords'].clear()
    text_format['title'].clear()
    text_format['thebibliography'].clear()
    text_format['avtore'].clear()
    text_format['abstracte'].clear()
    text_format['keywordse'].clear()
    text_format['naze'].clear()
    text_format['author_info'].clear()
    text_format['doi'].clear()
    text_format['bibliographyl'].clear()


def btnIn_click():
    dir = tkinter.filedialog.askopenfilename(filetypes=[("TeX files", "*.tex")])
    dir_target = dir
    if len(dir) > 0:
        inp.delete(0, END)
        inp.insert(0, dir)


def btnOut_click():
    dir = tkinter.filedialog.askdirectory()
    if len(dir) > 0:
        out.delete(0, END)
        out.insert(0, dir)


def btn_ready():
    if threads_num[0] != 0:
        return
    else:
        threads_num[0] += 1
        tex_proccesing = threading.Thread(target=run_convert)
        tex_proccesing.start()


def run_convert():
    get_author(inp.get())
    tex_dir = inp.get().split('/')[:-1]
    dir_main.append(tex_dir[len(tex_dir) - 1])
    cls_temp = ''
    for i in tex_dir:
        cls_temp += i + '/'
    tex_cls.append(cls_temp + 'isueps.cls')
    tex_dir.append(tex_path[0])
    str_to_dir_tex = ''
    for i in tex_dir:
        str_to_dir_tex += i + '/'
    get_page(inp.get()[:-3] + "toc")
    all_time = 0
    print("RUN INTO CONVERTER")
    for i in range(len(author)):
        temp_str_to_dir_tex = str_to_dir_tex + author[i] + '.tex'
        ch_time = time.monotonic()
        tex_to_text(temp_str_to_dir_tex, i)
        if not check_article[0]:
            continue
        print("PROCCESING " + temp_str_to_dir_tex + " FILE")
        lang = get_lang(temp_str_to_dir_tex)
        print("MAKING FILES: ", end='')
        if (lang == '1'):
            if comboExpansion.get() == 'txt':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.txt', i, ru_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.txt', i, eng_literals)
            elif comboExpansion.get() == 'html':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.html', i, ru_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.html', i, eng_literals)
            elif comboExpansion.get() == 'xml':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.xml', i, ru_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.xml', i, eng_literals)
        else:
            if comboExpansion.get() == 'txt':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.txt', i, eng_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.txt', i, ru_literals)
            elif comboExpansion.get() == 'html':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.html', i, eng_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.html', i, ru_literals)
            elif comboExpansion.get() == 'xml':
                export_first_half(out.get().replace('/', '\\') + '\\' + author[i] + '_eng.xml', i, eng_literals)
                export_second_half(out.get().replace('/', '\\') + '\\' + author[i] + '_ru.xml', i, ru_literals)
        clear_text_format()
        check_article[0] = False
        res = time.monotonic() - ch_time
        all_time += res
        print("succesful: {:>.3f}".format(res) + " seconds.")
    print("DONE:  " + out.get() + " in {:>.3f}".format(all_time) + " seconds.")
    mb.showinfo("Информация", "Программа завершена")
    author.clear()
    page.clear()
    tex_dir.clear()
    tex_path.clear()
    dir_main.clear()
    lang_type.clear()
    tex_cls.clear()
    threads_num[0] = 0


def get_author(main_tex_file):
    with open(main_tex_file) as a:
        for i in a:
            if i[0:6] == "\\input":
                str = re.search('{[^}]*}', i).group(0)
                strt = str.split('/')
                strt1 = strt[1].replace('}', '')
                if not tex_path:
                    tex_path.append(strt[0].replace('{', ''))
                author.append(strt1)


def get_page(toc_file):
    with open(toc_file) as f:
        for i in f:
            if i[0:13] == '\contentsline':
                str = re.split('\{', i)
                str = re.sub('[^0-9]', "", str[len(str) - 1])
                page.append(str)


lw_context_db = latexwalker.get_default_latex_context_db()
lw_context_db.add_context_category(
    'custom-macro',
    macros=[MacroSpec('udk', '{'),
            MacroSpec('msc', '{'),
            MacroSpec('keywordse', '{'),
            MacroSpec('avtore', '{'),
            MacroSpec('naze', '{'),
            MacroSpec('textbf', ''),
            MacroSpec('bibitem', '{'),
            MacroSpec('avtogl', '{{'),
            MacroSpec('avtogle', '{{'),
            MacroSpec('thanks', '{'),
            MacroSpec('setcounter', '{{'),
            MacroSpec('email', '{'),
            MacroSpec('-')]
)

l2w_context_db = latex2text.get_default_latex_context_db()
l2w_context_db.add_context_category(
    'custom-macro',
    prepend=True,
    macros=[MacroTextSpec('udk', simplify_repl='r"%(1)s"'),
            MacroTextSpec('msc', simplify_repl='r"%(1)s"'),
            MacroTextSpec('keywordse', simplify_repl='r"%(1)s"'),
            MacroTextSpec('avtore', simplify_repl='r"%(1)s"'),
            MacroTextSpec('naze', simplify_repl='r"%(1)s"'),
            MacroTextSpec('textbf', simplify_repl='%(1)s'),
            MacroTextSpec('setcounter', simplify_repl='r"%(1)s"'),
            MacroTextSpec('avtogl', simplify_repl=''),
            MacroTextSpec('avtogle', simplify_repl=''),
            MacroTextSpec('bibitem', simplify_repl='check'),
            MacroTextSpec('footnote', simplify_repl=''),
            MacroTextSpec('thanks', simplify_repl=''),
            MacroTextSpec('email', simplify_repl='%(1)s'),
            MacroTextSpec('-', simplify_repl='')]
)
lw_context_db.add_context_category('custom-env', environments=[EnvironmentSpec('thebibliography', '{'),
                                                               EnvironmentSpec('bibliographyl', '{')])
l2w_context_db.add_context_category('custom-env',
                                    environments=[EnvironmentTextSpec('thebibliography', simplify_repl='r"%(body)s"'),
                                                  EnvironmentTextSpec('bibliographyl', simplify_repl='r"%(body)s"')])


def get_lang(file_path):
    lang = -1
    with open(file_path, 'r') as f:
        for line in f:
            if re.search(r"\\setcounter{aqwe}{\d}", line):
                lang = re.search(r"\\setcounter{aqwe}{\d}", line).group(0)[-2]
                return lang
            else:
                continue
        return lang


def tex_to_text(file_path, author_num):
    s = []
    with open(file_path, 'r') as tf:
        str = tf.read()
        walker = LatexWalker(str, lw_context_db)
        converter = LatexNodes2Text(latex_context=l2w_context_db)
        (nodelist, pos, _len) = walker.get_latex_nodes()
        article_node = [nodelist[0]]
        for item in nodelist:
            if isinstance(item, LatexGroupNode) or isinstance(item, LatexEnvironmentNode):
                __article_catch(nodelist, article_node)
                break
        if not check_article[0]:
            return False
        s = __node_handler(article_node[0].nodelist, converter, walker)
        text = ''
        str = _doi_template(tex_cls[0])
        text_format['doi'] = [(str + page[author_num])]
        print(text_format['author'])
        print(text_format['udk'])
        print(text_format['msc'])
        print(text_format['abstract'])
        print(text_format['keywords'])
        print(text_format['title'])
        print(text_format['thebibliography'])
        ##print(text_format['bibliographyl'])
        print(text_format['avtore'])
        print(text_format['abstracte'])
        print(text_format['keywordse'])
        print(text_format['naze'])
        ##print(text_format['author_info'])
        print(text_format['doi'])
        return True


def __node_handler(_node_list, _converter, _walker):
    s = []
    for _item in _node_list:
        ##print(_item)
        if isinstance(_item, LatexGroupNode):
            s.append(__node_handler(_item.nodelist, _converter, _walker))
            continue
        if isinstance(_item, LatexEnvironmentNode):
            if _item.environmentname == 'thebibliography':
                thebibliography_pos_check[0] = _item.pos
                thebibliography_pos_check[1] = _item.pos + _item.len + 1
                thebibliography_pos_check[2] = 'thebibliography'
                text_format['thebibliography'].append(__node_handler(_item.nodelist, _converter, _walker))
            elif _item.environmentname == 'bibliographyl':
                thebibliography_pos_check[0] = _item.pos
                thebibliography_pos_check[1] = _item.pos + _item.len + 1
                thebibliography_pos_check[2] = 'bibliographyl'
                text_format['bibliographyl'].append(__node_handler(_item.nodelist, _converter, _walker))
            elif _item.environmentname == 'abstracte':
                text_format['abstracte'] = (__node_handler(_item.nodelist, _converter, _walker))
            elif _item.environmentname == 'abstract':
                text_format['abstract'] = (__node_handler(_item.nodelist, _converter, _walker))
            else:
                __node_handler(_item.nodelist, _converter, _walker)
        if isinstance(_item, LatexMacroNode):
            if _item.macroname == 'textbf':
                pos = _item.pos
                pos_to_next = _item.pos + _item.len + 1
                str_tmp = ''
                str_tmp += _converter.node_to_text(_item) + ','
                check_mail = False
                nodes, pos, len = _walker.get_latex_nodes(pos_to_next, read_max_nodes=20)
                for node in nodes:
                    if isinstance(node, LatexMacroNode):
                        if node.macroname == 'hfill' or node.macroname == 'textbf':
                            break
                        elif node.macroname == 'email':
                            check_mail = True
                            str_tmp += 'email: ' + _converter.node_to_text(node)
                        else:
                            str_tmp += _converter.node_to_text(node)
                    elif isinstance(node, LatexGroupNode):
                        if is_textbf_inside(node.nodelist):
                            break
                    else:
                        str_tmp += _converter.node_to_text(node)
                if check_mail or re.search(r"tel\.", str_tmp) or re.search(r"тел\.", str_tmp) or re.search(r"email",
                                                                                                           str_tmp):
                    text_format['author_info'].append(str_tmp)
            if _item.macroname == 'it' or _item.macroname == 'itshape' or _item.macroname == 'sl' or _item.macroname == 'em':
                pos = _item.pos
                if pos > thebibliography_pos_check[0] and pos < thebibliography_pos_check[1]:
                    pos_to_curs = _item.pos - 1
                    temp_nodes, pos, len = _walker.get_latex_nodes(pos_to_curs, read_max_nodes=1)
                    ##print(temp_nodes)
                    s.append('<i>' + _converter.node_to_text(temp_nodes[0]) + '</i>')
                    return s

            if _item.macroname == 'textit' or _item.macroname == 'emph':
                pos = _item.pos
                if pos > thebibliography_pos_check[0] and pos < thebibliography_pos_check[1]:
                    s.append('<i>' + _converter.node_to_text(_item) + '</i>')
                    continue
            obj_list = text_format.get(_item.macroname, 0)
            if not isinstance(obj_list, int):
                if _item.macroname == 'keywords':
                    text_format[_item.macroname].append(__node_handler(_item.nodeargd.argnlist, _converter, _walker))
                else:
                    text_format[_item.macroname] = (__node_handler(_item.nodeargd.argnlist, _converter, _walker))
        ts = _converter.node_to_text(_item)
        s.append(ts)
    return s


def is_textbf_inside(nodes):
    for item in nodes:
        if isinstance(item, LatexMacroNode):
            if item.macroname == 'textbf':
                return True
        elif isinstance(item, LatexGroupNode):
            cur_res = is_textbf_inside(item.nodelist)
            if not cur_res:
                continue
            else:
                return cur_res
    return False


def __article_catch(_nodelist, val):
    for _item in _nodelist:
        if isinstance(_item, LatexGroupNode):
            __article_catch(_item.nodelist, val)
        elif isinstance(_item, LatexEnvironmentNode):
            if _item.environmentname == 'article':
                val[0] = _item
                check_article[0] = True
            else:
                __article_catch(_item.nodelist, val)


def _doi_template(file_path):
    with open(file_path, 'r') as f:
        str = ''
        for line in f:
            if re.search(r"https://doi.org/[\d].*\\i", line):
                str = re.search(r"https://doi.org/[\d].*\\i", line).group(0)[:-2]
                break
        return str


def reference_maker(file, tf_key, switch_val):
    tmp = ''
    tmp_list = []
    tmp_count = 0
    for j in text_format[tf_key][switch_val]:
        tmp_count += 1
        if j == 'check':
            tmp_list.append(tmp)
            tmp = ''
        else:
            tmp = tmp.replace('\n', ' ')
            try:
                tmp += j
            except TypeError:
                tmp_obj = j[0]
                while (isinstance(tmp_obj, list)):
                    tmp_obj = tmp_obj[0]
                tmp += tmp_obj
        if tmp_count == len(text_format[tf_key][switch_val]):
            tmp_list.append(tmp)
            tmp = ''
    c = 1
    tmp = ''
    for i in tmp_list:
        tmp_t = i.replace('\n', '')
        tmp_t2 = tmp_t.replace(' ', '')
        if not tmp_t:
            continue
        if not tmp_t2:
            continue
        tmp = str(c) + ". " + tmp_t
        c += 1
        file.write(tmp + '\n')


def export_second_half(_file_export, author_num, literals):
    #print(_file_export)
    with io.open(_file_export, 'w', encoding="utf-8") as fout:
        if comboExpansion.get() == 'html':
            fout.write("<!DOCTYPE html>" + '\n')
            fout.write("<html>" + '\n')
            fout.write("<head>"
                       "<title>ISU</title>"
                       "<meta charset=\"UTF-8\">"
                       "</head>")
            fout.write("<body>")
            fout.write("<h2><div class=\"field-result\">")
            fout.write(''.join(text_format['naze'][0]).replace('\n', ' ') + '\n')
            fout.write("</div></h2><div class=\"cap\">")
            fout.write(literals[0])
            fout.write("</div> <div class=\"field-result\">")
            strtmp = ''
            for i in range(len(text_format['avtore'][0])):
                if (isinstance(text_format['avtore'][0][i], list)):
                    strtmp = ''.join(text_format['avtore'][0][i])
                    text_format['avtore'][0][i] = strtmp

            author_name = ''.join(text_format['avtore'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')

            fout.write("</div><div class=\"cap\">")
            fout.write(literals[1])
            fout.write("</div><div class=\"field-result\"><p>")
            temp = ''
            for i in text_format['abstracte']:
                temp += i
            fout.write(temp + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[2])
            fout.write("</div><div class=\"field-result\"><p>")
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i + len(text_format['author_info']) // 2])
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[3])
            fout.write("</div><div class=\"field-result\"><p>")
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])
            fout.write(author_name+ ', ' + ''.join(text_format['naze'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[7])
            fout.write("</div><div class=\"field-result\"><p>")
            if not text_format['keywordse']:
                if not text_format['keywords']:
                    fout.write('')
                else:
                    for i in text_format['keywords'][1]:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywordse']:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[8])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[9])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[10])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[11])
            fout.write("</div><div class=\"field-result\"><PRE>")
            if (len(text_format['bibliographyl']) == 1):
                reference_maker(fout, 'bibliographyl', 0)
            elif not text_format['bibliographyl']:
                if not text_format['thebibliography']:
                    fout.write('')
                elif len(text_format['thebibliography']) == 1:
                    reference_maker(fout, 'thebibliography', 0)
                elif len(text_format['thebibliography']) == 2:
                    reference_maker(fout, 'thebibliography', 1)
            elif (len(text_format['bibliographyl']) == 2):
                reference_maker(fout, 'bibliographyl', 1)
            fout.write("</PRE></body>")

        elif comboExpansion.get() == 'txt':
            strtmp = ''.join(text_format['naze'][0]).replace('\n', ' ')
            fout.write(strtmp + '\n')
            fout.write(literals[0])
            strtmp = ''
            for i in range(len(text_format['avtore'][0])):
                if (isinstance(text_format['avtore'][0][i], list)):
                    strtmp = ''.join(text_format['avtore'][0][i])
                    text_format['avtore'][0][i] = strtmp
            strtmp = ''.join(text_format['avtore'][0])

            author_name = ''.join(text_format['avtore'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')
            fout.write(literals[1])
            temp = ''
            for i in text_format['abstracte']:
                temp += i
            fout.write(temp + '\n')
            fout.write(literals[2])
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i + len(text_format['author_info']) // 2])
            fout.write(literals[3])
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])

            fout.write(author_name + ', ' + ''.join(text_format['naze'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            if not text_format['keywordse']:
                if not text_format['keywords']:
                    fout.write('')
                else:
                    for i in text_format['keywords'][1]:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywordse']:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write(literals[8])
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write(literals[9])
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write(literals[10])
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write(literals[11])
            if (len(text_format['bibliographyl']) == 1):
                reference_maker(fout, 'bibliographyl', 0)
            elif not text_format['bibliographyl']:
                if not text_format['thebibliography']:
                    fout.write('')
                elif len(text_format['thebibliography']) == 1:
                    reference_maker(fout, 'thebibliography', 0)
                elif len(text_format['thebibliography']) == 2:
                    reference_maker(fout, 'thebibliography', 1)
            elif (len(text_format['bibliographyl']) == 2):
                reference_maker(fout, 'bibliographyl', 1)

        elif comboExpansion.get() == 'xml':
            fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + '\n')
            fout.write("<naze>" + '\n')
            fout.write(''.join(text_format['naze'][0]).replace('\n', ' ') + '\n')
            fout.write("</naze>" + '\n' + "<" + literals[0][:-1] + ">" + '\n')
            strtmp = ''
            for i in range(len(text_format['avtore'][0])):
                if (isinstance(text_format['avtore'][0][i], list)):
                    strtmp = ''.join(text_format['avtore'][0][i])
                    text_format['avtore'][0][i] = strtmp
            strtmp = ''.join(text_format['avtore'][0])
            author_name = ''.join(text_format['avtore'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')

            fout.write("</" + literals[0][:-1] + ">" + '\n' + "<" + literals[1][:-1] + ">" + '\n')
            temp = ''
            for i in text_format['abstracte']:
                temp += i
            fout.write(temp + '\n')
            fout.write("</" + literals[1][:-1] + ">" + '\n' + "<" + literals[2][:-1] + ">" + '\n')
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i + len(text_format['author_info']) // 2])
            fout.write("</" + literals[2][:-1] + ">" + '\n' + "<" + literals[3][:-1] + ">" + '\n')
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])
            fout.write(author_name + ', ' + ''.join(text_format['naze'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            fout.write("</" + literals[3][:-1] + ">" + '\n' + "<" + literals[7][:-1] + ">" + '\n')
            if not text_format['keywordse']:
                if not text_format['keywords']:
                    fout.write('')
                else:
                    for i in text_format['keywords'][1]:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywordse']:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write("</" + literals[7][:-1] + ">" + '\n' + "<" + literals[8][:-1] + ">" + '\n')
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write("</" + literals[8][:-1] + ">" + '\n' + "<" + literals[9][:-1] + ">" + '\n')
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write("</" + literals[9][:-1] + ">" + '\n' + "<" + literals[10][:-1] + ">" + '\n')
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write("</" + literals[10][:-1] + ">" + '\n' + "<" + literals[11][:-1] + ">" + '\n')
            if (len(text_format['bibliographyl']) == 1):
                reference_maker(fout, 'bibliographyl', 0)
            elif not text_format['bibliographyl']:
                if not text_format['thebibliography']:
                    fout.write('')
                elif len(text_format['thebibliography']) == 1:
                    reference_maker(fout, 'thebibliography', 0)
                elif len(text_format['thebibliography']) == 2:
                    reference_maker(fout, 'thebibliography', 1)
            elif (len(text_format['bibliographyl']) == 2):
                reference_maker(fout, 'bibliographyl', 1)
            fout.write("</" + literals[11][:-1] + ">" + '\n')


def export_first_half(_file_export, author_num, literals):
    #print(_file_export)
    with io.open(_file_export, 'w', encoding="utf-8") as fout:
        if comboExpansion.get() == 'html':
            fout.write("<!DOCTYPE html>" + '\n')
            fout.write("<html>" + '\n')
            fout.write("<head>"
                       "<title>ISU</title>"
                       "<meta charset=\"UTF-8\">"
                       "</head>")
            fout.write("<body>")
            fout.write("<h2><div class=\"field-result\">")
            fout.write(''.join(text_format['title'][0]).replace('\n', ' ') + '\n')
            fout.write("</div></h2><div class=\"cap\">")
            fout.write(literals[0])
            fout.write("</div> <div class=\"field-result\">")
            for i in range(len(text_format['author'][0])):
                if (isinstance(text_format['author'][0][i], list)):
                    strtmp = ''.join(text_format['author'][0][i])
                    text_format['author'][0][i] = strtmp
            strtmp = ''.join(text_format['author'][0])
            author_name = ''.join(text_format['author'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')

            fout.write("</div><div class=\"cap\">")

            fout.write(literals[1])
            fout.write("</div><div class=\"field-result\"><p>")
            temp = ''
            for i in text_format['abstract']:
                temp += i
            fout.write(temp + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[2])
            fout.write("</div><div class=\"field-result\"><p>")
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i])
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[3])
            fout.write("</div><div class=\"field-result\"><p>")
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])
            fout.write(author_name+ ', ' + ''.join(text_format['title'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[7])
            fout.write("</div><div class=\"field-result\"><p>")
            if not text_format['keywords']:
                if not text_format['keywordse']:
                    fout.write('')
                else:
                    for i in text_format['keywordse']:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywords'][0]:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[8])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[9])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[10])
            fout.write("</div><div class=\"field-result\"><p>")
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write("</p></div><div class=\"cap\">")
            fout.write(literals[11])
            fout.write("</div><div class=\"field-result\"><PRE>")
            if (len(text_format['thebibliography']) == 1):
                reference_maker(fout, 'thebibliography', 0)
            elif not text_format['thebibliography']:
                if not text_format['bibliographyl']:
                    fout.write('')
                elif len(text_format['bibliographyl']) == 1:
                    reference_maker(fout, 'bibliograpghyl', 0)
                elif len(text_format['bibliographyl']) == 2:
                    reference_maker(fout, 'bibliograpghyl', 1)
            elif (len(text_format['thebibliography']) == 2):
                reference_maker(fout, 'thebibliography', 0)
            fout.write("</PRE></body>")

        elif comboExpansion.get() == 'txt':
            strtmp = ''.join(text_format['title'][0]).replace('\n', ' ')
            fout.write(strtmp + '\n')
            fout.write(literals[0])
            strtmp = ''
            for i in range(len(text_format['author'][0])):
                if (isinstance(text_format['author'][0][i], list)):
                    strtmp = ''.join(text_format['author'][0][i])
                    text_format['author'][0][i] = strtmp
            strtmp = ''.join(text_format['author'][0])

            author_name = ''.join(text_format['author'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')

            fout.write(literals[1])
            temp = ''
            for i in text_format['abstract']:
                temp += i
            fout.write(temp + '\n')
            fout.write(literals[2])
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i])
            fout.write(literals[3])
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])
            fout.write(author_name + ', ' + ''.join(text_format['title'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            fout.write(literals[7])
            if not text_format['keywords']:
                if not text_format['keywordse']:
                    fout.write('')
                else:
                    for i in text_format['keywordse']:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywords'][0]:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write(literals[8])
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write(literals[9])
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write(literals[10])
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write(literals[11])
            if (len(text_format['thebibliography']) == 1):
                reference_maker(fout, 'thebibliography', 0)
            elif not text_format['thebibliography']:
                if not text_format['bibliographyl']:
                    fout.write('')
                elif len(text_format['bibliographyl']) == 1:
                    reference_maker(fout, 'bibliograpghyl', 0)
                elif len(text_format['bibliographyl']) == 2:
                    reference_maker(fout, 'bibliograpghyl', 1)
            elif (len(text_format['thebibliography']) == 2):
                reference_maker(fout, 'thebibliography', 0)

        elif comboExpansion.get() == 'xml':
            fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + '\n')
            fout.write("<title>" + '\n')
            fout.write(''.join(text_format['title'][0]).replace('\n', ' ') + '\n')
            fout.write("</title>" + '\n' + "<" + literals[0][:-1] + ">" + '\n')
            strtmp = ''
            for i in range(len(text_format['author'][0])):
                if (isinstance(text_format['author'][0][i], list)):
                    strtmp = ''.join(text_format['author'][0][i])
                    text_format['author'][0][i] = strtmp
            strtmp = ''.join(text_format['author'][0])

            author_name = ''.join(text_format['author'][0][::-1])
            author_name = author_name.replace(',', '')
            author_name = author_name.replace('^', '')
            author_name = re.sub(r'\d', '', author_name)
            author_name = re.sub(r'\s+', ' ', author_name)

            for i in range(len(author_name)):
                if author_name[i] == '.' and (i + 1) < len(author_name) and author_name[i + 1] != " ":
                    author_name = author_name[:i + 1] + " " + author_name[i + 1:]

            fout.write(author_name + '\n')

            fout.write("</" + literals[0][:-1] + ">" + '\n' + "<" + literals[1][:-1] + ">" + '\n')
            temp = ''
            for i in text_format['abstract']:
                temp += i
            fout.write(temp + '\n')
            fout.write("</" + literals[1][:-1] + ">" + '\n' + "<" + literals[2][:-1] + ">" + '\n')
            for i in range(len(text_format['author_info']) // 2):
                fout.write(text_format['author_info'][i])
            fout.write("</" + literals[2][:-1] + ">" + '\n' + "<" + literals[3][:-1] + ">" + '\n')
            tmp_list = tex_path[0].split('-')
            year = tmp_list[0]
            volume = tmp_list[len(tmp_list) - 1]
            volume = volume.replace('t', '')
            if (author_num + 1 != len(page)):
                pages = str(page[author_num]) + '-' + str(int(page[author_num + 1]) - 1) + '.'
            else:
                pages = str(page[author_num])
            fout.write(author_name + ', ' + ''.join(text_format['title'][0]).replace('\n', ' ') +
                       literals[12] + literals[4] + str(year) + literals[5] + str(volume) + literals[
                           6] + pages + ' ' + str(text_format['doi'][0]) + '\n')
            fout.write("</" + literals[3][:-1] + ">" + '\n' + "<" + literals[7][:-1] + ">" + '\n')
            if not text_format['keywords']:
                if not text_format['keywordse']:
                    fout.write('')
                else:
                    for i in text_format['keywordse']:
                        fout.write(str(i[0]))
            else:
                for i in text_format['keywords'][0]:
                    fout.write(str(i[0]))
            fout.write('\n')
            fout.write("</" + literals[7][:-1] + ">" + '\n' + "<" + literals[8][:-1] + ">" + '\n')
            fout.write(str(text_format['udk'][0][0]) + '\n')
            fout.write("</" + literals[8][:-1] + ">" + '\n' + "<" + literals[9][:-1] + ">" + '\n')
            fout.write(str(text_format['msc'][0][0]) + '\n')
            fout.write("</" + literals[9][:-1] + ">" + '\n' + "<" + literals[10][:-1] + ">" + '\n')
            fout.write(str(text_format['doi'][0]) + '\n')
            fout.write("</" + literals[10][:-1] + ">" + '\n' + "<" + literals[11][:-1] + ">" + '\n')
            if (len(text_format['thebibliography']) == 1):
                reference_maker(fout, 'thebibliography', 0)
            elif not text_format['thebibliography']:
                if not text_format['bibliographyl']:
                    fout.write('')
                elif len(text_format['bibliographyl']) == 1:
                    reference_maker(fout, 'bibliograpghyl', 0)
                elif len(text_format['bibliographyl']) == 2:
                    reference_maker(fout, 'bibliograpghyl', 1)
            elif (len(text_format['thebibliography']) == 2):
                reference_maker(fout, 'thebibliography', 0)
            fout.write("</" + literals[11][:-1] + ">" + '\n')

# interface

root['bg'] = 'black'
root.title('Annotation Maker')
root.geometry('400x300')
root.resizable(width=False, height=False)

canvas = Canvas(root, height=300, width=400, bg='#fafafa')
canvas.pack()

frame = Frame(root, bg="#fafafa")
frame.place(rely=0.1, relwidth=1, relheight=1)

txt1 = Label(frame, text='Укажите путь к основному TeX файлу', bg="#fafafa")
txt1.place(relx=0.05, rely=0)

inp = Entry(frame, bg='white', width=50)
inp.insert(0, 'C:\\')
inp.place(relx=0.1, rely=0.1)

txt2 = Label(frame, text='Укажите путь к папке для отображения результата', bg="#fafafa")
txt2.place(relx=0.05, rely=0.2)

out = Entry(frame, bg='white', width=50)
out.insert(0, 'C:\\')
out.place(relx=0.1, rely=0.3)

image = ImageTk.PhotoImage(file="1.jpg")

btnIn = Button(frame, text='папка', command=btnIn_click, width=40, relief='flat', image=image, bg="#fafafa")
btnIn.place(relx=0.8, rely=0.07)

btnOut = Button(frame, text='папка', command=btnOut_click, width=40, relief='flat', image=image, bg="#fafafa")
btnOut.place(relx=0.8, rely=0.27)

txt3 = Label(frame, text='Укажите расширение для конечных файлов', bg="#fafafa")
txt3.place(relx=0.05, rely=0.4)
comboExpansion = ttk.Combobox(frame, state="readonly",
                              values=[
                                  "txt",
                                  "html",
                                  "xml"
                              ])
comboExpansion.current(0)
comboExpansion.place(relx=0.1, rely=0.5)

btnReady = Button(frame, text='выполнить', bg='white', command=btn_ready, width=12)
btnReady.place(relx=0.7, rely=0.7)


root.mainloop()
