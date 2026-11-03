"""Standard-library checks for the committed participant PowerPoint."""
import io
import re
import unittest
import zipfile
from xml.etree import ElementTree as ET

from build_workshop_powerpoint import (
    FONT, NS, OUTPUT, ROOT, font_errors, japanese_spacing, spacing_errors, validate_sources,
)
from check_public_hygiene import _inspect_text


class WorkshopPowerPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = (ROOT / OUTPUT).read_bytes()

    def test_fonts_across_entire_package(self):
        self.assertEqual(font_errors(self.payload), [])

    def test_spacing_everywhere_including_notes_and_credit(self):
        self.assertEqual(spacing_errors(self.payload), [])
        self.assertEqual(
            japanese_spacing('FabricのPlanを180分で説明。日本語  23枚。'),
            'Fabric の Plan を 180 分で説明。日本語 23 枚。',
        )
        self.assertEqual(japanese_spacing('「Plan」（180）を確認。'),
                         '「Plan」（180）を確認。')
        stable = 'https://example.com/Lab09?id=180 / COPY INTO / Power BI / FY2026'
        self.assertEqual(japanese_spacing(stable), stable)
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            cover = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
            texts = [node.text for node in cover.findall('.//a:t', NS)]
            self.assertIn('Jiayi Yang, Swarm Data SE', texts)
            for number in range(1, 24):
                slide = ET.fromstring(archive.read(f'ppt/slides/slide{number}.xml'))
                self.assertIn('Jiayi Yang, Swarm Data SE',
                              [node.text for node in slide.findall('.//a:t', NS)])
            billing = ET.fromstring(archive.read('ppt/slides/slide8.xml'))
            billing_text = '\n'.join(node.text or '' for node in billing.findall('.//a:t', NS))
            self.assertIn('30 日間の 1 セッションは 847 CU 時間', billing_text)
            self.assertNotIn('730', billing_text)

    def test_font_auditor_rejects_theme_and_run_regressions(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as source:
            for target, old, new in [
                ('ppt/theme/theme1.xml', b'Yu Gothic UI', b'Aptos'),
                ('ppt/slides/slide1.xml', b'Yu Gothic UI', b'Calibri'),
                ('ppt/notesSlides/notesSlide1.xml', b'Yu Gothic UI', b'MS Gothic'),
            ]:
                output = io.BytesIO()
                with zipfile.ZipFile(output, 'w') as changed:
                    for name in source.namelist():
                        data = source.read(name)
                        if name == target:
                            data = data.replace(old, new, 1)
                        changed.writestr(name, data)
                self.assertTrue(font_errors(output.getvalue()), target)

    def test_slide_count_content_provenance_and_public_hygiene(self):
        sources = validate_sources(ROOT)
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            slides = sorted(name for name in archive.namelist()
                            if re.fullmatch(r'ppt/slides/slide\d+\.xml', name))
            self.assertEqual(len(slides), 23)
            text = '\n'.join(
                entry.text or '' for name in slides
                for entry in ET.fromstring(archive.read(name)).findall('.//a:t', NS)
            )
            for number in range(10):
                self.assertIn(f'Lab{number:02d}', text)
            for forbidden in ('未確認', '未検証', '原因未特定', '講師向けガイド',
                              'FACILITATOR-GUIDE', 'UNCONFIRMED-ITEMS', '解答'):
                self.assertNotIn(forbidden, text)
            for required in ('途中で終了できません', '847 CU 時間', 'From Sheets',
                             '日付キー', '165 分', '180 分', '合成 CSV', 'Preview',
                             'Q4 / Q4a', '公式認定', 'Diego Diaz', 'Jiayi Yang'):
                self.assertIn(required, text)
            for name in archive.namelist():
                if name.endswith('.xml') or name.endswith('.rels'):
                    root = ET.fromstring(archive.read(name))
                    # OPC extension / table-style GUIDs are template structure, not
                    # customer identifiers. Audit text and external targets instead.
                    public = '\n'.join(element.text or '' for element in root.iter()
                                       if element.tag.rsplit('}', 1)[-1] != 'tableStyleId')
                    targets = '\n'.join(element.get('Target', '') for element in root.iter()
                                        if element.get('TargetMode') == 'External')
                    self.assertEqual(_inspect_text(name, public + targets), [], name)
            notes = '\n'.join(
                entry.text or '' for name in archive.namelist()
                if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', name)
                for entry in ET.fromstring(archive.read(name)).findall('.//a:t', NS)
            )
            for source in sources:
                self.assertIn('/blob/main/' + source, notes)
            # These are provenance hashes at generation time, not a requirement
            # to rebuild a curated deck after unrelated source housekeeping.
            self.assertEqual(len(re.findall(r'出典 SHA256: [a-f0-9]{64}', notes)), 23)

    def test_visible_shapes_stay_on_slide_and_icons_are_not_distorted(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
            size = presentation.find('p:sldSz', NS)
            width, height = int(size.get('cx')), int(size.get('cy'))
            icons = 0
            screenshots = 0
            diagram_arrows = 0
            for name in archive.namelist():
                if not re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
                    continue
                root = ET.fromstring(archive.read(name))
                diagram_arrows += sum(
                    shape.get('prst') in ('rightArrow', 'downArrow', 'upArrow')
                    for shape in root.findall('.//a:prstGeom', NS)
                )
                for transform in root.findall('.//a:xfrm', NS):
                    offset, extent = transform.find('a:off', NS), transform.find('a:ext', NS)
                    if offset is None or extent is None:
                        continue
                    x, y = int(offset.get('x')), int(offset.get('y'))
                    w, h = int(extent.get('cx')), int(extent.get('cy'))
                    self.assertGreaterEqual(min(x, y), 0, name)
                    self.assertLessEqual(x + w, width + 1, name)
                    self.assertLessEqual(y + h, height + 1, name)
                for picture in root.findall('.//p:pic', NS):
                    props = picture.find('p:nvPicPr/p:cNvPr', NS)
                    description = props.get('descr', '')
                    if description.startswith('Microsoft Fabric公式アイコン'):
                        icons += 1
                        transform = picture.find('p:spPr/a:xfrm', NS)
                        extent = transform.find('a:ext', NS)
                        self.assertEqual(extent.get('cx'), extent.get('cy'))
                        self.assertIsNone(picture.find('.//a:srcRect', NS))
                        self.assertNotIn('rot', transform.attrib)
                        self.assertNotIn('flipH', transform.attrib)
                        self.assertNotIn('flipV', transform.attrib)
                    elif '画面例' in description:
                        screenshots += 1
            self.assertGreaterEqual(icons, 60)
            self.assertEqual(screenshots, 5)
            self.assertGreaterEqual(diagram_arrows, 12)

    def test_all_visible_runs_have_explicit_sizes_and_no_autofit(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            for name in archive.namelist():
                if not re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
                    continue
                root = ET.fromstring(archive.read(name))
                for run in root.findall('.//a:r', NS):
                    props = run.find('a:rPr', NS)
                    self.assertIsNotNone(props.get('sz'), name)
                    self.assertGreaterEqual(int(props.get('sz')), 1000, name)
                for tag in ('normAutofit', 'spAutoFit'):
                    self.assertEqual(root.findall(f'.//a:{tag}', NS), [], name)
            self.assertEqual(FONT, 'Yu Gothic UI')


if __name__ == '__main__':
    unittest.main()
