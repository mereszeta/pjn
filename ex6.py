from pywnxml.WNQuery import WNQuery


def main():
    query = WNQuery('/Users/gszereme/Downloads/plwordnet_3_1/plwordnet-3.1-visdisc.xml')
    pairs = [(("szkoda", 2), ("wypadek", 1)), (("kolizja", 2), ("szkoda majątkowa", 1)),
             (("nieszczęście", 2), ("katastrofa budowlana", 1))]
    for pair in pairs:
        s1, s2 = query.lookUpSense(pair[0][0], pair[0][1], "n").wnid, query.lookUpSense(pair[1][0], pair[1][1],
                                                                                        "n").wnid
        print(pair[0][0], pair[1][0], query.simLeaCho(s1, s2, 'n', 'hypernym', True))


if __name__ == '__main__':
    main()
