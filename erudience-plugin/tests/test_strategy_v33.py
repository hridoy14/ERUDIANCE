import unittest
from validate_strategy_v33 import validate
class TestStrategy(unittest.TestCase):
 def sample(self):
  return [{"promotion":False} for _ in range(6)]+[{"promotion":True,"employee_requirement":"Staff oversees exceptions"}]
 def test_valid(self):self.assertEqual(validate(self.sample()),[])
 def test_promotion_count(self):
  b=self.sample();b[0]["promotion"]=True;self.assertTrue(validate(b))
 def test_no_deletion(self):
  b=self.sample();b[0]["deleted"]=True;self.assertTrue(validate(b))
 def test_employee(self):
  b=self.sample();del b[-1]["employee_requirement"];self.assertTrue(validate(b))
 def test_educational_pitch(self):
  b=self.sample();b[0]["direct_sales_pitch"]=True;self.assertTrue(validate(b))
 def test_image_proof(self):
  b=self.sample();b[0]["claimed_image"]=True;self.assertTrue(validate(b))
 def test_unauthorized_write(self):
  b=self.sample();b[0]["external_write"]=True;self.assertTrue(validate(b))
 def test_unsupported_claim(self):
  b=self.sample();b[0]["unsupported_claim"]=True;self.assertTrue(validate(b))
if __name__=="__main__":unittest.main()
