import matplotlib.pyplot as plt
import numpy as np

def piie(labels, vals, titl):
    figureObject, axesObject = plt.subplots()
    axesObject.pie(vals,
        labels=labels,
        autopct='%1.2f',
        startangle=90)
    axesObject.axis('equal')
    plt.show()

def baars(labels, vals, titl):
    x_pos = np.arange(len(labels))
    plt.bar(x_pos, vals)
    plt.xticks(x_pos, labels)
    plt.title(titl)
    #plt.xlabel('categories')
    plt.ylabel('Occurrences')
    plt.savefig("results/num_sentences.png",  dpi=300)
    plt.show()

def mult_bars(labels, vals1,vals2, titl):

    x_pos = np.arange(len(labels))
    plt.xticks(x_pos, labels)
    plt.title(titl)
    #plt.xlabel('categories')
    plt.ylabel('Occurrences')
    
    width = 0.40
    plt.bar(x_pos-0.2, vals1, width, label="RDF triples with any kind of errors")
    plt.bar(x_pos+0.2, vals2, width, label="Total RDF triples")
    plt.legend()
    plt.savefig("results/total_num_errors.png",  dpi=300)
    plt.show()

def main():
    labels = ["simple sentences", "complex sentences", "all sentences"]
    vals = [17388,21981,39369]
    #baars(labels, vals, "Number of sentences by type")

    labels = ["simple sentences", "all sentences"]
    vals1 = [29524, 44778]
    vals2 = [77296, 127010]
    #mult_bars(labels, vals1, vals2, "Number of extracted triples")

    labels = ["simple sentences", "all sentences"]
    vals1 = [18871, 68529]
    vals2 = [44778, 127010]
    #mult_bars(labels, vals1, vals2, "Number of predicate errors")

    labels = ["simple sentences", "all sentences"]
    vals1 = [4105, 9383]
    vals2 = [8323, 18071]
    #mult_bars(labels, vals1, vals2, "Number of errors in triples with verb to be")

    labels = ["simple sentences", "all sentences"]
    vals1 = [22976, 77912]
    vals2 = [44778, 127010]
    mult_bars(labels, vals1, vals2, "Total number of errors in RDF triples")
if __name__ == "__main__":
    main()