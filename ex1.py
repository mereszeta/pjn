import os
import regex


def ex1():
    rgx = r'\b[Uu]st[a-z]+\s+z\s+dnia\s+(\d{1,2}\s+\p{L}+\s+\d{4})\s*r\.\s+[o\-]\s+(\b[\p{L}+\s+]+)\s+(\(Dz\.\s*U\.(' \
          r'?:\s*(?:oraz\s*)?(?:z\s*\d{4}\s*r\.)?\s*(?:(?:(?:Nr\.?\s*\d+,?)*\s*poz\.\s*\d+,?\s*[i]?)\s*)*)*\)) '
    inner_regex = r'((?:z\s*\d{4}\s*r\.)?\s*(?:(?:(?:Nr\.?\s*\d+,?)*\s*poz\.\s*\d+,?\s*[i]?)\s*))'
    inner_regex_2 = r'(?:(?:z\s*(\d{4})\s*r\.)?\s*(?:(?:(?:Nr\.?\s*(\d+),?)*\s*poz\.\s*(\d+),?\s*[i]?)\s*))'
    res_list = []
    for filename in os.listdir(os.getcwd() + '/ustawy'):
        with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
            out = ' '.join(file.readlines())
            out = out.replace('\\n', '')
            res = regex.findall(rgx, out,flags=regex.DOTALL)
            for r in res:
                res2 = regex.findall(inner_regex, r[2])
                for r2 in res2:
                    res3 = regex.findall(inner_regex_2, r2)
                    if len(res3) != 0:
                        year = r[0][-4:]
                        number = '1'
                        if res3[0][0] != '':
                            year = res3[0][0]
                        if res3[0][1] != '':
                            number = res3[0][1]
                        res_list.append((year, number, res3[0][2]))
    final = [(i, res_list.count(i)) for i in set(res_list)]
    final.sort(reverse=True, key=lambda x: x[1])
    str_res = ""
    for f in final:
        str_res += str(f)
        str_res += "\n"
    with open('result.txt', 'w', encoding='utf-8') as res:
        res.write(str_res)


def ex2():
    rgx=r'(?:\s*[Aa]rt\.\s+(\d+)(?:.*[Uu]st\.\s+(\d+)))'
    # rgx = r'art\.\s*(\d+)[a-z]?\s*ust\.\s*(\d+)|(?!<\s{4,})art\.\s*(\d+)[a-z]?|[aA]rt\.\s*(\d+)[a-z]?.*ust\.\s*(\d+)'
    filename='2001_973.txt'
    with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
        out = ' '.join(file.readlines())
        out = out.replace('\\n', '')
        res = regex.findall(rgx, out)
        final = [(i, res.count(i)) for i in set(res)]
        final.sort(reverse=True, key=lambda x: x[1])
        print(final)


def ex3():
    rgx = r'\b[Uu]staw(?:(?:ie)|(?:om)|(?:ami)|(?:ach)|[ayęąo]?)\b'
    count = 0
    for filename in os.listdir(os.getcwd() + '/ustawy'):
        with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
            out = ' '.join(file.readlines())
            out = out.replace('\\n', '')
            res = regex.findall(rgx, out)
            count += len(res)
    print(count)


if __name__ == "__main__":
    ex2()
