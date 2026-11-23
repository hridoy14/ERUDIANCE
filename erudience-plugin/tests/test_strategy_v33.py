import unittest
from validate_strategy_v33 import validate,validate_single_slot
class TestSingleSlot(unittest.TestCase):
 def test_valid_educational(self):self.assertEqual(validate_single_slot({"promotion":False}),[])
 def test_valid_promotion(self):self.assertEqual(validate_single_slot({"promotion":True,"employee_requirement":"Staff oversees exceptions"}),[])
 def test_promotion_needs_employee(self):self.assertIn("Promotion missing employee requirement",validate_single_slot({"promotion":True}))
 def test_educational_pitch(self):self.assertIn("Educational slot contains direct pitch",validate_single_slot({"promotion":False,"direct_sales_pitch":True}))
 def test_promotion_may_pitch(self):self.assertEqual(validate_single_slot({"promotion":True,"employee_requirement":"x","direct_sales_pitch":True}),[])
 def test_unsupported_claim(self):self.assertIn("Unsupported claim",validate_single_slot({"unsupported_claim":True}))
 def test_unauthorized_write(self):self.assertIn("Unauthorized write",validate_single_slot({"external_write":True}))
 def test_authorized_write(self):self.assertEqual(validate_single_slot({"external_write":True,"explicit_authorization":True}),[])
 def test_deleted(self):self.assertIn("Topic deletion forbidden",validate_single_slot({"deleted":True}))
 def test_invalid_slot(self):self.assertEqual(validate_single_slot("nope"),["INVALID_SLOT"])
 def test_matches_batch_validator(self):
  slot={"promotion":True}
  self.assertEqual(validate_single_slot(slot),[e for e in validate([{"promotion":False} for _ in range(6)]+[slot]) if "promotion" in e.lower() or "employee" in e.lower()])
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
