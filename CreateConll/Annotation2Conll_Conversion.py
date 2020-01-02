import re
from tokenizer import tokenize
from spacy.pipeline import SentenceSegmenter
from spacy.pipeline import Sentencizer
from spacy.lang.en import English
sentence_segmenter = English()
sentencizer = sentence_segmenter.create_pipe("sentencizer")
sentence_segmenter.add_pipe(sentencizer)

#bean class to hold annotation attributes
class Annotation():
    def __init__(self, doc_name, begin, end, entity_text, entity_type, add_to_conll=False):
        self.doc_name = doc_name
        self.begin = begin
        self.end = end
        self.entity_text = entity_text
        self.entity_type = entity_type
        self.add_to_conll = add_to_conll
    def __str__(self):
        return self.doc_name + ' ' + str(self.begin) + ' ' + str(self.end) + ' ' + self.entity_text + ' ' + self.entity_type
    def __eq__(self,other):
        return self.begin == other.begin and self.end == other.end \
                and self.entity_text == other.entity_text and self.entity_type == other.entity_type

# Read the annotation from DB
# You can change this method if your annotation in stored in a file 
def read_annotations():
	import pymysql
	db=pymysql.connect("localhost","root","******","NER_Annotation")
	cursor=db.cursor()
    annotation_list = []
    #doc_name, begin, end, entity_text, entity_type
    querry = "SELECT DISTINCT docname, begin, end, entity_text, new_entity_type from Entity_Info_3_new where iserror=0"
    cursor.execute(querry)
    resultset=cursor.fetchall()
    annotation_list = []
    for res in resultset:
        docname = res[0]
        annotation = Annotation(docname, res[1], res[2], res[3], res[4])
        if docname not in doc_2_annotation.keys():
            doc_2_annotation[docname] = []
        doc_2_annotation[docname].append(annotation)
    return doc_2_annotation

# get BIO-entity_type from annotation
def get_type(annotation_list, begin, end):
    for antn in annotation_list:
        antn_type = antn.entity_type
        antn_begin = antn.begin
        antn_end = antn.end
        if begin <= antn_begin and antn_begin < end:
            antn.add_to_conll = True
            return 'B-'+antn_type
        elif (antn_begin < begin and begin < antn_end) or (antn_begin < end  and end <= antn_end):
            #antn.add_to_conll = True
            return 'I-'+antn_type
    return "O"

# check for annotation error of overlap entity
# to remove the overlap annotation 
# "X Y Z" -> Name
# "X Y" -> Name
def remove_overlap_anotn(annotation_list):
    flag = False
    for x in annotation_list:
        for y in annotation_list:
            if x != y:
                if x.begin <= y.begin and y.end < x.end:
                    print("Overlap: ")
                    print(str(y) + "is a part of \n" + str(x))
                    annotation_list.remove(y)
    return annotation_list 

# to check if any annotation is missed in conll
def check_annotation_not_added_in_Conll(annotation_list):
    for x in annotation_list:
        if not x.add_to_conll:
            print(str(x)) 

if __name__ = "__main__":
	out_conll_path = "out.conll"
	# docs used in annotations
	doc_path = 'docs/'
	writer = open(out_conll_path, 'w')
	for doc_name in doc_2_annotation.keys():
	    annotation_list = doc_2_annotation[doc_name]
	    annotation_list = remove_overlap_anotn(annotation_list)
	    doc = open(doc_path+doc_name).read() 
	    entity_idx = 0
	    prev_tag = ''
	    offset = 0
	    # considering '\n' as sen
	    for paragraph in doc.split('\n'):#text_sentences.sents:
	        text_sentences = sentence_segmenter(paragraph)
	        for sentence in text_sentences.sents:
	            if sentence.text.strip():
	                # special case to handle 
	                # Dr. J . is tokenized as ["Dr.", "J."], Utlimately you will not find J. in doc
	                for word in sentence.text.strip().split():
	                    tokens_ = list(tokenize(word))
	                    tokens = []
	                    # 2 September2011 is tokenized as ["2 September 2011"], Utlimately you will not find September 2011 in doc
	                    for tok in tokens_:
	                        if tok.txt is not None:
	                            tokens.extend(tok.txt.split())
	                    for token in tokens:
	                        if token == None:
	                            continue
	                        offset = doc.find(token, offset)
	                        begin = offset
	                        end = offset + len(token)
	                        offset += len(token)
	                        if begin == -1:
	                            print("Begin starts with -1")
	                            print(str(token) + '\t' + str(begin) + '\t' + str(end)  + '\t' + doc_name+'\t'+entity_type+'\n')
	                        entity_type = get_type(annotation_list, begin, end)
	                        writer.write(str(token) + '\t' + str(begin) + '\t' + str(end)  + '\t' + doc_name+'\t'+entity_type+'\n')
	                writer.write('\n')
	    check_annotation_not_added_in_Conll(annotation_list)                
	writer.flush()
