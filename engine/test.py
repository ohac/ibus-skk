# -*- coding: utf-8 -*-

from __future__ import with_statement
import unittest
import os, os.path
import skk

class TestSKK(unittest.TestCase):
    def setUp(self):
        # Make sure to start with new empty usrdict.
        usrdict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    ".skk-ibus-jisyo")
        try:
            os.unlink(usrdict_path)
        except:
            pass

        sysdict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "skk-ibus-jisyo")
        s_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "SKK-JISYO.S")
        if not os.path.exists(sysdict_path):
            if not os.path.exists(s_dict_path):
                raise RuntimeError('SKK-JISYO.S not found; do "wget http://openlab.ring.gr.jp/skk/skk/dic/SKK-JISYO.S"')
            with open(sysdict_path, 'a') as tp:
                with open(s_dict_path, 'r') as fp:
                    for line in fp:
                        tp.write(line)
                        if line.startswith(';; okuri-nasi'):
                            tp.write(u'#/# /#0月#0日/#1／#1/#1月#1日/\n'.encode('EUC-JP'))
                            tp.write(u'#ひき /#1匹/#3匹/#0匹/#2匹/\n'.encode('EUC-JP'))
                        if line.startswith('greek '):
                            tp.write(u'request /リクエスト/\n'.encode('EUC-JP'))

        self.__skk = skk.Context(usrdict=skk.UsrDict(usrdict_path),
                                 sysdict=skk.SysDict(sysdict_path),
                                 candidate_selector=skk.CandidateSelector())

    def testusrdict(self):
        usrdict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    ".skk-ibus-jisyo-corrupted")
        with open(usrdict_path, 'w+') as fp:
            fp.write(u'あい /愛/\n'.encode('EUC-JP'))
        try:
            usrdict = skk.UsrDict(usrdict_path, 'UTF-8')
            self.assertNotEqual(usrdict, None)
            self.assertTrue(usrdict.read_only)
        except Exception, e:
            self.fail("can't open user dictionary: %s" % e.message)
        finally:
            os.unlink(usrdict_path)

    def testinputmodechange(self):
        self.__skk.reset()
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_NONE)
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        # catch ctrl-j in HIRAGANA
        handled, output = self.__skk.press_key(u'ctrl+j')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HIRAGANA)
        # HIRAGANA to KATAKANA
        handled, output = self.__skk.press_key(u'q')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_KATAKANA)
        # catch ctrl-j in KATAKANA, and be still in KATAKANA
        self.__skk.press_key(u'ctrl+j')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_KATAKANA)
        # KATAKANA to HIRAGANA
        handled, output = self.__skk.press_key(u'q')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HIRAGANA)
        # HIRAGANA to LATIN
        handled, output = self.__skk.press_key(u'l')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_LATIN)
        # 'q' letter in LATIN
        handled, output = self.__skk.press_key(u'q')
        self.assertFalse(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_LATIN)
        # LATIN to HIRAGANA
        handled, output = self.__skk.press_key(u'ctrl+j')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HIRAGANA)
        # HIRAGANA to WIDE-LATIN
        handled, output = self.__skk.press_key(u'shift+l')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_WIDE_LATIN)
        # 'q' letter in WIDE-LATIN
        handled, output = self.__skk.press_key(u'q')
        self.assert_(handled)
        self.assertEqual(output, u'ｑ')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_WIDE_LATIN)
        # WIDE-LATIN to HIRAGANA
        handled, output = self.__skk.press_key(u'ctrl+j')
        self.assert_(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HIRAGANA)
        # wwl -> っ and HIRAGANA to LATIN
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'w')
        handled, output = self.__skk.press_key(u'w')
        self.assertTrue(handled)
        self.assertEqual(output, u'っ')
        self.assertEqual(self.__skk.preedit, u'w')
        handled, output = self.__skk.press_key(u'l')
        self.assertTrue(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_LATIN)

    def testromkana(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        # ka -> か
        self.assertEqual(self.__skk.press_key(u'k'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'k')
        self.assertEqual(self.__skk.press_key(u'a'), (True, u'か'))
        self.assertEqual(self.__skk.preedit, u'')
        # myo -> みょ
        self.assertEqual(self.__skk.press_key(u'm'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'm')
        self.assertEqual(self.__skk.press_key(u'y'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'my')
        self.assertEqual(self.__skk.press_key(u'o'), (True, u'みょ'))
        self.assertEqual(self.__skk.preedit, u'')
        # toggle submode to katakana
        self.assertEqual(self.__skk.press_key(u'q'), (True, u''))
        # ka -> カ
        self.assertEqual(self.__skk.press_key(u'k'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'k')
        self.assertEqual(self.__skk.press_key(u'a'), (True, u'カ'))
        self.assertEqual(self.__skk.preedit, u'')
        # nX -> ンX
        self.__skk.press_key(u'n')
        self.assertEqual(self.__skk.press_key(u'.'), (True, u'ン。'))
        # ww -> っw
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'w')
        handled, output = self.__skk.press_key(u'w')
        self.assertTrue(handled)
        self.assertEqual(output, u'っ')
        self.assertEqual(self.__skk.preedit, u'w')
        # zl -> →
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'z')
        self.assertEqual(self.__skk.press_key(u'l'), (True, u'→'))

    def testhiraganakatakana(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_START)
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.press_key(u'q'), (True, u'アイ'))
        self.assertEqual(self.__skk.preedit, u'')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'q')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_KATAKANA)
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_START)
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.press_key(u'q'), (True, u'あい'))
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_KATAKANA)
        self.assertEqual(self.__skk.conv_state, skk.CONV_STATE_NONE)
        self.assertEqual(self.__skk.preedit, u'')
        # う゛-> ヴ
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+v')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽う゛')
        self.assertEqual(self.__skk.press_key(u'q'), (True, u'ヴ'))
        # ヴ -> う゛
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_KATAKANA)
        self.__skk.press_key(u'shift+v')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽ヴ')
        self.assertEqual(self.__skk.press_key(u'q'), (True, u'う゛'))
        # ▽nq -> ン
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+q')
        self.__skk.press_key(u'n')
        handled, output = self.__skk.press_key(u'q')
        self.assertTrue(handled)
        self.assertEqual(output, u'ン')

    def testokurinasi(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.assertEqual(self.__skk.press_key(u'shift+a'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.assertEqual(self.__skk.press_key(u'i'), (True, u''))
        self.assertEqual(self.__skk.preedit, u'▽あい')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼愛')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼哀')

    def testegglikenewline(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        # CONV_STATE_START
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.__skk.egg_like_newline = False
        self.assertEqual(self.__skk.press_key(u'return'), (True, u'あい\n'))
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.__skk.egg_like_newline = True
        self.assertEqual(self.__skk.press_key(u'return'), (True, u'あい'))
        # CONV_STATE_SELECT
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u' ')
        self.__skk.egg_like_newline = False
        self.assertEqual(self.__skk.press_key(u'return'), (True, u'愛\n'))
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u' ')
        self.__skk.egg_like_newline = True
        self.assertEqual(self.__skk.press_key(u'return'), (True, u'愛'))

    def testokuriari(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'g')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+e')
        self.assertEqual(self.__skk.preedit, u'▼考え')
        self.assertEqual(self.__skk.press_key(u'r'), (True, u'考え'))
        self.assertEqual(self.__skk.preedit, u'r')
        self.assertEqual(self.__skk.press_key(u'u'), (True, u'る'))

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+h')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+z')
        self.assertEqual(self.__skk.preedit, u'▽は*z')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▼恥ず')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+t')
        self.__skk.press_key(u'u')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+t')
        self.__skk.press_key(u't')
        self.assertEqual(self.__skk.preedit, u'▽つか*っt')

        # Debian Bug#591052
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'shift+j')
        self.assertEqual(self.__skk.preedit, u'▽かん*j')

        # Issue#10
        self.__skk.debug = True
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+f')
        self.__skk.press_key(u'u')
        self.__skk.press_key(u'shift+n')
        self.__skk.press_key(u'd')
        self.__skk.press_key(u'a')
        self.assertEqual(self.__skk.preedit, u'▼踏んだ')
        self.__skk.debug = False

    def testcompletion(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あい')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        self.__skk.press_key(u' ')
        self.__skk.kakutei()
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        self.__skk.press_key(u' ')
        self.__skk.kakutei()
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'ctrl+i')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')

    def testautoconvesion(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.preedit, u'▽あい')
        self.__skk.press_key(u',')
        self.assertEqual(self.__skk.preedit, u'▼愛、')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼哀、')
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u'w')
        self.__skk.press_key(u'o')
        self.assertEqual(self.__skk.preedit, u'▼愛を')

    def testdelete(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        handled, output = self.__skk.press_key(u'backspace')
        self.assertTrue(handled)
        self.assertEqual(self.__skk.preedit, u'▽')
        handled, output = self.__skk.press_key(u'backspace')
        self.assertTrue(handled)
        self.assertEqual(self.__skk.preedit, u'')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u's')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u't')
        self.__skk.press_key(u's')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼挨拶')
        handled, output = self.__skk.press_key(u'backspace')
        self.assertTrue(handled)
        self.assertEqual(output, u'挨')
        handled, output = self.__skk.press_key(u'backspace')
        self.assertFalse(handled)

    def testdeleteshortcut(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        handled, output = self.__skk.press_key(u'ctrl+h')
        self.assertTrue(handled)
        self.assertEqual(self.__skk.preedit, u'▽')
        handled, output = self.__skk.press_key(u'ctrl+h')
        self.assertTrue(handled)
        self.assertEqual(self.__skk.preedit, u'')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u's')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u't')
        self.__skk.press_key(u's')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼挨拶')
        handled, output = self.__skk.press_key(u'ctrl+h')
        self.assertTrue(handled)
        self.assertEqual(output, u'挨')
        handled, output = self.__skk.press_key(u'ctrl+h')
        self.assertFalse(handled)

    def testnumeric(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+q')
        self.assertEqual(self.__skk.preedit, u'▽')
        self.__skk.press_key(u'5')
        self.__skk.press_key(u'/')
        self.__skk.press_key(u'1')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼5月1日')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+q')
        self.__skk.press_key(u'5')
        self.__skk.press_key(u'h')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼５匹')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼五匹')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+q')
        self.assertEqual(self.__skk.preedit, u'▽')
        self.__skk.press_key(u'5')
        self.__skk.press_key(u'0')
        self.__skk.press_key(u'0')
        self.__skk.press_key(u'0')
        self.__skk.press_key(u'0')
        self.__skk.press_key(u'h')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼五万匹')

    def testkzik(self):
        self.__skk.reset()
        self.__skk.rom_kana_rule = skk.ROM_KANA_KZIK
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'b')
        self.__skk.press_key(u'g')
        handled, output = self.__skk.press_key(u'd')
        self.assertTrue(handled)
        self.assertEqual(output, u'びぇん')
        self.__skk.press_key(u's')
        handled, output = self.__skk.press_key(u'q')
        self.assertTrue(handled)
        self.assertEqual(output, u'さい')
        self.__skk.press_key(u'd')
        handled, output = self.__skk.press_key(u'l')
        self.assertTrue(handled)
        self.assertEqual(output, u'どん')
        self.__skk.rom_kana_rule = skk.ROM_KANA_NORMAL
        self.__skk.reset()

    def testdictedit(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'p')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ')
        self.__skk.press_key(u'a')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ あ')
        self.__skk.press_key(u'backspace')
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'ctrl+j')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ あ')
        self.__skk.press_key(u'backspace')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ▽か')
        self.__skk.press_key(u'return')
        self.__skk.press_key(u'backspace')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'p')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'[[DictEdit]] かぱ ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ▽かぱ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ')
        # Don't register empty string (Debian Bug#590191)
        self.__skk.press_key(u'return')
        self.assertEqual(self.__skk.preedit, u'▽かぱ')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ▽か')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ▼下')
        self.__skk.press_key(u'shift+h')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u'return')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'backspace')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ 下破')
        self.assertEqual(self.__skk.press_key(u'return'), (True, u'下破'))
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'p')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼下破')
        # Purge "下破" from the user dictionary (Debian Bug#590188).
        self.__skk.press_key(u'shift+x')
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'p')
        self.__skk.press_key(u'a')
        self.assertEqual(self.__skk.preedit, u'▽かぱ')
        self.__skk.press_key(u' ')
        # Should enter dict-edit since "下破" is purged above.
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かぱ ')
        self.__skk.press_key(u'ctrl+g')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'j')
        self.__skk.press_key(u'i')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'▼幹事')
        self.__skk.press_key(u'return')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'g')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+e')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かんが*え ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'▼考え')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'▽かんがえ')
        self.__skk.press_key(u'shift+e')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かんがえ*え ')
        self.__skk.press_key(u'ctrl+g')
        self.assertEqual(self.__skk.preedit, u'▽かんがええ')
        self.__skk.press_key(u'ctrl+h')
        self.assertEqual(self.__skk.preedit, u'▽かんがえ')
        self.__skk.press_key(u'ctrl+h')
        self.assertEqual(self.__skk.preedit, u'▽かんが')
        self.__skk.press_key(u'ctrl+g')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u't')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u' ')
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u't')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'q')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かたかな カタカナ')
        self.__skk.press_key(u'backspace')
        self.__skk.press_key(u'l')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'a')
        self.assertEqual(self.__skk.preedit, u'[DictEdit] かたかな カタカna')
        # http://github.com/ueno/ibus-skk/issues/#issue/4
        handled, output = self.__skk.press_key(u'ctrl+m')
        self.assertEqual(output, u'カタカna')

    def testhankaku(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_KATAKANA)
        self.__skk.press_key(u'ctrl+q')
        self.assertEqual(self.__skk.input_mode, skk.INPUT_MODE_HANKAKU_KATAKANA)
        self.__skk.press_key(u'shift+z')
        self.__skk.press_key(u'e')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽ｾﾞﾝｶｸ')
        handled, output = self.__skk.press_key(u'ctrl+q')
        self.assertTrue(handled)
        self.assertEqual(output, u'ゼンカク')
        self.__skk.press_key(u'shift+z')
        self.__skk.press_key(u'e')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▽ｾﾞﾝｶｸ')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼全角')

    def testabbrev(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'/')
        self.__skk.press_key(u'r')
        self.__skk.press_key(u'e')
        self.__skk.press_key(u'q')
        self.__skk.press_key(u'u')
        self.__skk.press_key(u'e')
        self.__skk.press_key(u's')
        self.__skk.press_key(u't')
        self.assertEqual(self.__skk.preedit, u'▽request')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼リクエスト')
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'z')
        handled, output = self.__skk.press_key(u'/')
        self.assertTrue(handled)
        self.assertEqual(output, u'・')

        self.__skk.reset();
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'/')
        handled, output = self.__skk.press_key(u']')
        self.assertTrue(handled)
        self.assertEqual(output, u'')
        self.assertEqual(self.__skk.preedit, u'▽]')

    def testkuten(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'\\')
        self.assertEqual(self.__skk.preedit, u'Kuten([MM]KKTT) ')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'backspace')
        self.assertEqual(self.__skk.preedit, u'Kuten([MM]KKTT) ')
        self.__skk.press_key(u'backspace')
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'\\')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'1')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'2')
        handled, output = self.__skk.press_key(u'return')
        self.assertTrue(handled)
        self.assertEqual(output, u'、')
        # Don't start KUTEN input on {wide,}latin input mode.
        self.__skk.activate_input_mode(skk.INPUT_MODE_LATIN)
        handled, output = self.__skk.press_key(u'\\')
        self.assertFalse(handled)
        self.assertEqual(output, u'')
        self.__skk.activate_input_mode(skk.INPUT_MODE_WIDE_LATIN)
        handled, output = self.__skk.press_key(u'\\')
        self.assertTrue(handled)
        self.assertEqual(output, u'＼')

if __name__ == '__main__':
    unittest.main()
