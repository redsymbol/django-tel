import unittest
from django.template import Template, Context
from templatetags import tel

class Test_tel_filter(unittest.TestCase):
    def test_main(self):
        testdata = [
            {'value' : u'4155551212',
             'out'   : u'<a href="tel:+14155551212">4155551212</a>',
             },
            {'value' : u'415-555-1212',
             'out'   : u'<a href="tel:+14155551212">415-555-1212</a>',
             },
            {'value' : u'(415)555-1212',
             'out'   : u'<a href="tel:+14155551212">(415)555-1212</a>',
             },
            # convert letters
            {'value' : u'415-555-ROCK',
             'out'   : u'<a href="tel:+14155557625">415-555-ROCK</a>',
             },
            {'value' : u'415-555-rock',
             'out'   : u'<a href="tel:+14155557625">415-555-rock</a>',
             },
            {'value' : u'415-555-roCK',
             'out'   : u'<a href="tel:+14155557625">415-555-roCK</a>',
             },
            {'value' : u'415-JKL-ROCK',
             'out'   : u'<a href="tel:+14155557625">415-JKL-ROCK</a>',
             },
            {'value' : u'415-JJJ-WXYZ',
             'out'   : u'<a href="tel:+14155559999">415-JJJ-WXYZ</a>',
             },
            {'value' : u'800-2-Buy-Now',
             'out'   : u'<a href="tel:+18002289669">800-2-Buy-Now</a>',
             },
            # chop off excess digits
            {'value' : u'800-BUY-IT-NOW',
             'out'   : u'<a href="tel:+18002894866">800-BUY-IT-NOW</a>',
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = tel.tel(td['value'])
            msg = 'e: "%s", a: "%s" [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

    def test_safe(self):
        """verify that html is not escaped"""
        t = Template('{% load tel %}{{"4155551212"|tel}}')
        self.assertEqual('<a href="tel:+14155551212">4155551212</a>', t.render(Context()))

    def test_garbage_in(self):
        """verify that unsafe input is caught"""
        t = Template(u'{% load tel %}{{somevar|tel}}')
        c = {'somevar' : "\"<foo>'blah' &copy; \"bloof\"</foo>\""}
        self.assertEqual(u'&quot;&lt;foo&gt;&#39;blah&#39; &amp;copy; &quot;bloof&quot;&lt;/foo&gt;&quot;',
                         t.render(Context(c)))

    def test_varsub(self):
        """Verify variable substitution works"""
        t = Template('{% load tel %}{{somevar|tel}}')
        self.assertEqual('<a href="tel:+14155551212">4155551212</a>', t.render(Context({'somevar' : '4155551212'})))

class Test_telify_tag(unittest.TestCase):
    def test_telify_text(self):
        testdata = [
            # degenerate cases
            {'in'  : '',
             'out' : '',
             },
            {'in'  : 'something',
             'out' : 'something',
             },
            {'in'  : '<p><strong>Not</strong> a phone number.</p>',
             'out' : '<p><strong>Not</strong> a phone number.</p>',
             },
            # single phone number
            {'in'  : '800.555.1212',
             'out' : '<a href="tel:+18005551212">800.555.1212</a>',
             },
            {'in'  : '800-555-1212',
             'out' : '<a href="tel:+18005551212">800-555-1212</a>',
             },
            {'in'  : 'Call 800-555-1212 today',
             'out' : 'Call <a href="tel:+18005551212">800-555-1212</a> today',
             },
            # multiple phone numbers
            {'in'  : 'Call 800-555-1212 today.  But do not call 800-555-1213, that is for losers!',
             'out' : 'Call <a href="tel:+18005551212">800-555-1212</a> today.  But do not call <a href="tel:+18005551213">800-555-1213</a>, that is for losers!',
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = tel.telify_text(td['in'])
            msg = 'e: "%s", a: "%s" [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

    def test_phone_finding(self):
        "Checks on phone number finding (regex matching)"
        testdata = [
            {'text'   : '',
             'phones' : [],
             },
            {'text'   : '800-222-3333',
             'phones' : ['800-222-3333'],
             },
            {'text'   : '800-222-3333\n800-333-4444',
             'phones' : ['800-222-3333', '800-333-4444'],
             },
            {'text'   : '800.222.3333\n800-333-4444',
             'phones' : ['800.222.3333', '800-333-4444'],
             },
            {'text'   : '800.222.3333',
             'phones' : ['800.222.3333'],
             },
            {'text'   : '(800)222-3333',
             'phones' : ['(800)222-3333'],
             },
            {'text'   : '800-222-3333\n(667)682-7767',
             'phones' : ['800-222-3333', '(667)682-7767'],
             },
            {'text'   : 'Can the regex find the number 800-222-3333 in this block',
             'phones' : ['800-222-3333'],
             },
            {'text'   : 'Can the regex find the number 8002223333 in this block',
             'phones' : ['8002223333'],
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['phones']
            actual = tel.PHONE_RE.findall(td['text'])
            msg = 'e: "%s", a: "%s" [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)
            
    def test_block(self):
        """verify that telify block actually works as advertised"""
        testdata = [
            {'content' : '4155551212',
             'out'     : '<a href="tel:+14155551212">4155551212</a>',
             },
            {'content' : '(415)555-1212',
             'out'     : '<a href="tel:+14155551212">(415)555-1212</a>',
             },
            {'content' : '<p>(415)555-1212</p>\n<p>667.682.7767</p>',
             'out'     : '<p><a href="tel:+14155551212">(415)555-1212</a></p>\n<p><a href="tel:+16676827767">667.682.7767</a></p>',
             },
            ]
        for ii, td in enumerate(testdata):
            t = Template('{% load tel %}{% telify %}' + td['content'] + '{% endtelify %}')
            expected = td['out']
            actual = t.render(Context())
            msg = 'e: "%s", a: "%s" [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

