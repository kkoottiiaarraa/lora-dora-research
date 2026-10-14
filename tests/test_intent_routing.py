import unittest
from lora_dora_study.intent_routing import gold_id,chat_messages,extract_id


class IntentRoutingTests(unittest.TestCase):
    def test_permutation_changes_id_without_changing_answer(self):
        tools=[dict(name='route',description='Directions'),dict(name='call',description='Phone')]
        example=dict(user_request='Phone home',available_tools=tools,answer='CALL')
        self.assertEqual(gold_id(example),'b')
        self.assertEqual(gold_id(dict(example,available_tools=list(reversed(tools)))),'a')
        messages=chat_messages(example,'router',True)
        self.assertEqual(messages[-1],dict(role='assistant',content='b'))
        self.assertIn('b | call | Phone\nUser Request:',messages[1]['content'])
        self.assertEqual(gold_id(dict(example,answer='none')),'-')
        with self.assertRaises(ValueError):gold_id(dict(example,answer='missing'))
        with self.assertRaises(ValueError):gold_id(dict(example,available_tools=[tools[0],tools[0]]))

    def test_uppercase_ids_and_garbage_are_not_silently_remapped(self):
        example=dict(user_request='x',available_tools=[dict(name=f't{i}',description='x') for i in range(28)],answer='t27')
        self.assertEqual(gold_id(example),'B')
        self.assertEqual(extract_id('<think>not a label</think>\nSelected Tool: **B**'),'B')
        self.assertEqual(extract_id('b'),'b')
        self.assertEqual(extract_id('call_handler'),'call_handler')
        self.assertEqual(extract_id('   -'),'−'.replace('−','-'))
        self.assertEqual(extract_id(''),'')


if __name__=='__main__':unittest.main()
