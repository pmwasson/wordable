import string

class ByteArray:
    def __init__(self):
        self.data = [0]
        self.bit = 0

    def push(self,size,data):
        data &= (1<<size)-1
        remaining = 8-self.bit
        if (size <= remaining):
            self.data[-1] |= data<<(remaining-size)
            self.bit += size
            if (self.bit >= 8):
                self.data.append(0)
                self.bit -= 8
        else:
            self.push(remaining,data>>(size-remaining))
            self.push(size-remaining,data)

    def append(self,ba):
        for b in ba.data[0:-1]:
            self.push(8,b)
        self.push(ba.bit,ba.data[-1]>>(8-ba.bit))

    def dump(self):
        return([hex(self.data[x]) for x in range(len(self.data))])

class Encode:
    def __init__(self,freq_order,pattern):
        self.bitsize = {}
        self.encode = {}

        range0 = 0
        range1 = 0

        for x in range(len(pattern)):
            range0 = range1
            range1 += pattern[x][0]
            val = 0

            for c in freq_order[range0:range1]:
                self.bitsize[c] = pattern[x][1]
                self.encode[c] = pattern[x][2] + val*2
                val += 1

    def member(self,entry):
        return(entry in self.bitsize)

    def size(self,entry):
        return(self.bitsize[entry])

    def data(self,entry,cbit):
        return(self.encode[entry] + cbit)


class Freq:
    def __init__(self):
        self.data = {}

    def insert(self,key):
        if not key in self.data.keys():
            self.data[key] = 0
        self.data[key] += 1

    def order(self):
        return([x[0] for x in sorted(self.data.items(),key=lambda x:x[1],reverse=True)])

class Tree:

    def __init__(self):
        self.child = {}

    def insert(self, key):
        if not key in self.child.keys():
            self.child[key] = Tree()
        return(self.child[key])

    def size(self,encode,depth=0):
        tsum = 0
        nextDepth = depth+1
        if (depth >= 5):
            nextDepth = 5
        for c in self.child.keys():
            if not encode[depth].member(c):
                print("Error:",c,"not found at depth",depth)
            tsum += encode[depth].size(c) + self.child[c].size(encode,nextDepth)
        return(tsum)

    def dump(self):
        result = ""
        children = list(self.child.keys())
        for c in children:
            result += c
            if (c is children[-1]):
                result += "!"
            result += self.child[c].dump()
        return(result)

    def dumpbin(self,encode,depth=0):
        result =ByteArray()
        children = list(self.child.keys())
        for c in children:
            stop = 0
            if (c is children[-1]):
                stop = 1
            result.push(encode[depth].size(c),encode[depth].data(c,stop))
            result.append(self.child[c].dumpbin(encode,depth+1))
        return(result)

    def read(self,wordfile,freq):
        wordcount = 0

        # read words
        with open(wordfile) as f:
            lines = f.readlines()

        # Put into tree
        for line in sorted(lines):
            if (len(line) != 6):
                print("Ignoring line: ",line.rstrip())
                continue
            wordcount += 1
            t = self
            for i in range(5):
                t = t.insert(line[i])
                freq[i].insert(line[i])
                freq[5].insert(line[i])
        return(wordcount)

def main():

    # 0-4 for letter position, use 5 for total
    freq = [Freq() for i in range(6)]
    total_freq = Freq()


    wordlist1 = Tree()
    wordlist2 = Tree()
    count1 = wordlist1.read("wordlist1.txt",freq) # Solution words
    count2 = wordlist2.read("wordlist2.txt",freq) # Guess words
    outputfile = "output.h"

    # Set letter frequency

    print("Letter frequency:")
    freq_ordered =[freq[i].order() for i in range(6)]


    # Encoding: prefix(0|1), enumeration(x), continue(c)

    # Bad encoding of 6-bits per letter
    scheme0 = [[26,6]]

    # 4 bit encoding: 0xxc       - 4 letter encodings
    # 6 bit encoding: 10xxxc     - 8 letter encodings
    # 7 bit encoding: 11xxxxc    - 16 letter encodings
    #                              28 letters (2 extras)
    scheme1 = [[4,4],[8,6],[14,7]]

    # 4 bit encoding: 0xxc       - 4 letter encodings
    # 6 bit encoding: 1xxxxc     - 15 letter encodings
    # 9 bit encoding: 11111xxxc  - 8 letter encodings
    #                              27 letters (1 extras)
    scheme2 = [[4,4],[15,6],[7,9]]

    # 4 bit encoding: 0xxc       - 4 letter encodings
    # 6 bit encoding: 1xxxxc     - 14 letter encodings
    # 8 bit encoding: 1111xxxc   - 8 letter encodings
    #                              26 letters
    scheme3 = [[4,4,0b0000],[14,6,0b100000],[8,8,0b11110000]]

    # 3 bit encoding: 0xc        - 2 letter encodings
    # 6 bit encoding: 10xxxc     - 8 letter encodings
    # 7 bit encoding: 11xxxxc    - 16 letter encodings
    #                              26 letters
    scheme4 = [[2,3],[8,6],[16,7]]

    # 3 bit encoding: xxc        - 3 letter encodings
    # 7 bit encoding: 110xxxc    - 8 letter encodings
    # 8 bit encoding: 111xxxxc   - 16 letter encodings
    #                              27 letters
    scheme5 = [[3,3],[8,7],[16,8]]


    # 4 bit encoding: xxxc       - 6 letter encodings
    # 7 bit encoding: 110xxxc    - 8 letter encodings
    # 8 bit encoding: 111xxxxc   - 12 letter encodings
    #                              31 letters
    scheme6 = [[6,4],[8,8],[12,9]]

    # Results:
    #
    # scheme bits (global)  bits (per position)
    # 1      133547         130078
    # 2      132021 *       128854
    # 3      132228         128388 *
    # 4      134410         131264

    encode = [Encode(freq_ordered[i], scheme3) for i in range(6)]

    for i in range(6):
        if (i < 5):
            print("Positional for position",i)
        else:
            print("Total")
        for c in freq_ordered[i]:
            print(c,":",encode[i].size(c),"bits","(",freq[i].data[c]," occurrences)")

    # Display stats

    total_count = count1 + count2
    print("Read",total_count,"words, ",total_count*5,"letters")

    dump = wordlist1.dump() + wordlist2.dump()
    end_count = dump.count("!")
    dump_len = len(dump) - end_count
    print("Entries",dump_len,"(",dump_len/(total_count*5),")")
    print("c-bits==0",end_count,"(",end_count / dump_len,")")


    final_size = wordlist1.size(encode) + wordlist2.size(encode) # pass in depth of 5 for total, remove for per letter

    print(final_size, "bits")
    print(final_size/8, "bytes")
    print(final_size/total_count,"bits per word")
    print(final_size/dump_len,"bits per entry")
    print(final_size/(5*total_count),"bits per letter")


    print("Writing",outputfile)
    with open(outputfile,"w") as writefile:
        writefile.write("// Generated output\n")
        writefile.write("const unsigned char PROGMEM wordlist1[] = {\n")
        writefile.write(",".join(wordlist1.dumpbin(encode).dump()));
        writefile.write("\n};\n")
        writefile.write("const unsigned char PROGMEM wordlist2[] = {\n")
        writefile.write(",".join(wordlist2.dumpbin(encode).dump()));
        writefile.write("\n};\n")

main();