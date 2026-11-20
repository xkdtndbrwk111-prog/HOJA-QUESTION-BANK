import unittest,sys,tempfile,random
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from convert import *

def question(i,t='MCQ'):
 q={'id':f'q{i}','type':t,'text':f'question {i}','answer':2 if t=='MCQ' else True if t=='OX' else 'answer'}
 if t=='MCQ':q['choices']=['a','b','c','d']
 return q
def bank(groups,subject='과학'):
 return convert_v1({'schemaVersion':1,'id':'test','title':'test','subject':subject,'groups':[{'id':f'g{i}','questions':g} for i,g in enumerate(groups)]})
class Contract(unittest.TestCase):
 def test_24(self):self.assertFalse(validate(bank([[question(i)] for i in range(24)]))['minimum25'])
 def test_25(self):self.assertTrue(validate(bank([[question(i)] for i in range(25)]))['structuralGate'])
 def test_mixed_group_count(self):self.assertEqual(validate(bank([[question(i)] for i in range(15)]+[[question(100+3*i+j) for j in range(3)] for i in range(10)]))['soloUnits'],25)
 def test_100_not_25(self):self.assertEqual(validate(bank([[question(5*i+j) for j in range(5)] for i in range(20)]))['soloUnits'],20)
 def test_short_not_solo(self):
  a=validate(bank([[question(i)] for i in range(24)]+[[question(99,'SHORT')]]));self.assertEqual((a['soloUnits'],a['teamUnits']),(24,25))
 def test_group_mix(self):self.assertEqual(validate(bank([[question(1,'SHORT'),question(2,'OX')]]))['soloUnits'],1)
 def test_stable_answer(self):
  q=bank([[question(1)]])['questions'][0];r=random.Random(42)
  for _ in range(100):
   opts=deepcopy(q['choices']);r.shuffle(opts);opts=[o for o in opts if o['id']==q['answer']['choiceId']]+[o for o in opts if o['id']!=q['answer']['choiceId']][:2];r.shuffle(opts);self.assertEqual(next(o for o in opts if o['id']==q['answer']['choiceId'])['content'][0]['text'],'c')
 def test_wrong_answer(self):
  b=bank([[question(1)]]);b['questions'][0]['answer']={'choiceId':'missing'}
  with self.assertRaises(ValueError):validate(b)
 def test_duplicate_choice(self):
  b=bank([[question(1)]]);b['questions'][0]['choices'][1]['content']=b['questions'][0]['choices'][0]['content'];self.assertEqual(validate(b)['issues'][0]['code'],'duplicate_choice')
 def test_fraction_equivalence(self):
  q=question(1);q['choices']=['[[frac:1/2]]','0.5','3/4','1/4'];self.assertEqual(validate(bank([[q]],'수학'))['issues'][0]['code'],'equivalent_numeric_choice')
 def test_fraction_representation(self):
  q=question(1);q['choices']=['1/2','2/4','3/4','1/4'];q['answerForm']='representation';self.assertEqual(validate(bank([[q]],'수학'))['issues'],[])
 def test_zero_denominator(self):
  q=question(1,'OX');q['text']='[[frac:1/0]]';self.assertEqual(validate(bank([[q]],'수학'))['issues'][0]['code'],'invalid_fraction')
 def test_path_escape(self):
  q=question(1,'OX');q['media']=[{'kind':'image','src':'assets/../evil.svg','alt':'x'}]
  with self.assertRaises(ValueError):bank([[q]])
 def test_missing_asset(self):
  q=question(1,'OX');q['media']=[{'kind':'image','src':'assets/bar.svg','alt':'x'}]
  with tempfile.TemporaryDirectory() as d:self.assertEqual(validate(bank([[q]]),Path(d))['issues'][0]['code'],'missing_or_unsafe_asset')
 def test_rich_refuses_flat(self):
  q=question(1,'OX');q['media']=[{'kind':'image','src':'assets/bar.svg','alt':'x'}]
  with self.assertRaises(ValueError):export_flat(bank([[q]]))
 def test_frequency_lengths(self):
  q=question(1);q['stimulus']={'kind':'frequency','period':'week','labels':['Mon','Tue'],'marks':[True]};self.assertEqual(validate(bank([[q]]))['issues'][0]['code'],'frequency_length')
 def test_flat_1_based(self):
  f={'questionSchemaVersion':2,'sourceSheetVersion':2,'cartridgeId':'123','questions':[{'num':1,'sourceNum':1,'familyId':'g','familyOrder':1,'variantType':'multiple','type':'MULTIPLE','question':'q','answer':'4','options':['a','b','c','d'],'isNull':False}]};b=convert_flat(f,'legacy');self.assertEqual(b['questions'][0]['answer']['choiceId'],'c4');self.assertEqual(export_flat(b)['questions'][0]['answer'],'4')
 def test_ox_bool(self):self.assertEqual(export_flat(bank([[question(1,'OX')]]))['questions'][0]['answer'],'O')
 def test_no_duplicate_question_id(self):
  with self.assertRaises(ValueError):validate(bank([[question(1)],[question(1)]]))
 def test_unknown_fields_fail(self):
  q=question(1);q['unknown']='x'
  with self.assertRaises(ValueError):bank([[q]])
if __name__=='__main__':unittest.main(verbosity=2)
