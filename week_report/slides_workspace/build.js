const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/liziming/.claude/skills/pptx/scripts/html2pptx');
const path = require('path');
const DIR = __dirname;

const H = { fill: { color: '0D3B4C' }, color: 'FFFFFF', bold: true, fontSize: 7, align: 'center', valign: 'middle' };
const C = { fill: { color: '243342' }, color: 'ECEFF1', fontSize: 6.5, align: 'center', valign: 'middle' };
const CL = { ...C, align: 'left' };
const E = { fill: { color: '1A3A3A' }, color: '2AA198', fontSize: 6.5, bold: true, align: 'center', valign: 'middle' };
const EL = { ...E, align: 'left' };
const R = { ...C, color: 'E74C3C' };

function c(sr, cost, opts = C) { return { text: `${sr} / ${cost}`, options: opts }; }

async function build() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'Weekly Report 2026-03-23 — EAAG Paper Overview';

  // Slides 1-3
  await html2pptx(path.join(DIR, 'slide01_title.html'), pptx);
  await html2pptx(path.join(DIR, 'slide02_insight.html'), pptx);
  await html2pptx(path.join(DIR, 'slide03_method.html'), pptx);

  // Slide 4: Datasets
  const { slide: s4, placeholders: p4 } = await html2pptx(path.join(DIR, 'slide04_datasets.html'), pptx);
  const DH = { fill: { color: '0D3B4C' }, color: 'FFFFFF', bold: true, fontSize: 8, align: 'center', valign: 'middle' };
  const DC = { fill: { color: '243342' }, color: 'ECEFF1', fontSize: 7, align: 'center', valign: 'middle' };
  const DCL = { ...DC, align: 'left' };
  const mt = p4.find(p => p.id === 'main-table');
  if (mt) {
    s4.addTable([
      [{ text: 'Environment', options: DH }, { text: 'Type', options: DH }, { text: 'Base SR', options: DH }, { text: 'Always SR', options: DH }, { text: 'Delta', options: DH }, { text: 'Optimizer', options: DH }, { text: 'Unc. Type', options: DH }, { text: 'Dataset Paper', options: DH }],
      [{ text: 'HotpotQA', options: DCL }, { text: 'Multi-hop QA', options: DCL }, { text: '49.0%', options: DC }, { text: '97.0%', options: DC }, { text: '+48.0', options: DC }, { text: 'Per-action eval', options: DCL }, { text: 'Type I', options: DC }, { text: 'Yang+ EMNLP18', options: DCL }],
      [{ text: 'FEVER', options: DCL }, { text: 'Fact Verif.', options: DCL }, { text: '37.0%', options: DC }, { text: '99.8%', options: DC }, { text: '+62.8', options: DC }, { text: 'Per-action eval', options: DCL }, { text: 'Type I', options: DC }, { text: 'Thorne+ NAACL18', options: DCL }],
      [{ text: 'APPS Intro', options: DCL }, { text: 'Code Gen', options: DCL }, { text: '58.5%', options: DC }, { text: '64.5%', options: DC }, { text: '+6.0', options: DC }, { text: 'K-variant', options: DCL }, { text: 'Mixed', options: DC }, { text: 'Hendrycks+ NeurIPS21', options: DCL }],
      [{ text: 'WebShop', options: DCL }, { text: 'Web Shop', options: DCL }, { text: '7.2%', options: DC }, { text: '43.0%', options: DC }, { text: '+35.8', options: DC }, { text: 'LLM-Propose-K', options: DCL }, { text: 'Mixed', options: DC }, { text: 'Yao+ NeurIPS22', options: DCL }],
      [{ text: 'TWExpress', options: DCL }, { text: 'Text Game', options: DCL }, { text: '67.5%', options: DC }, { text: '99.3%', options: DC }, { text: '+31.8', options: DC }, { text: 'Per-action eval', options: DCL }, { text: 'Type I', options: DC }, { text: 'Jansen+ EACL23', options: DCL }],
      [{ text: 'Plancraft', options: DCL }, { text: 'Mfg. Plan', options: DCL }, { text: '29.8%', options: DC }, { text: '22.8%', options: { ...DC, color: 'E6A817' } }, { text: '-7.0', options: { ...DC, color: 'E6A817' } }, { text: 'Per-action eval', options: DCL }, { text: 'Weak (harmful)', options: { ...DC, color: 'E6A817' } }, { text: 'Dag+ arXiv24', options: DCL }],
    ], { ...mt, border: { pt: 0.5, color: '3A4A5E' }, colW: [1.05, 0.8, 0.65, 0.7, 0.55, 1.0, 0.85, 1.25], rowH: [0.28, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24], autoPage: false });
  }
  const at = p4.find(p => p.id === 'appendix-table');
  if (at) {
    s4.addTable([
      [{ text: 'APPS Interview', options: DCL }, { text: 'Code Gen (hard)', options: DCL }, { text: '60.5%', options: DC }, { text: '79.5%', options: DC }, { text: '+19.0', options: DC }, { text: 'K-variant', options: DCL }, { text: 'Type D', options: DC }, { text: 'Hendrycks+ NeurIPS21', options: DCL }],
      [{ text: 'CRUXEval', options: DCL }, { text: 'Code Reason', options: DCL }, { text: '85.0%', options: DC }, { text: '99.5%', options: DC }, { text: '+14.5', options: DC }, { text: 'K-variant', options: DCL }, { text: 'Weak', options: DC }, { text: 'Gu+ ICML24', options: DCL }],
    ], { ...at, border: { pt: 0.5, color: '3A4A5E' }, colW: [1.05, 0.8, 0.65, 0.7, 0.55, 1.0, 0.85, 1.25], rowH: [0.24, 0.24], autoPage: false });
  }

  // Slide 5: Baselines
  const { slide: s5, placeholders: p5 } = await html2pptx(path.join(DIR, 'slide05_baselines.html'), pptx);
  const bt = p5.find(p => p.id === 'baseline-table');
  if (bt) {
    const bH = { fill: { color: '0D3B4C' }, color: 'FFFFFF', bold: true, fontSize: 8, align: 'center', valign: 'middle' };
    const bC = { fill: { color: '243342' }, color: 'ECEFF1', fontSize: 7.5, align: 'center', valign: 'middle' };
    const bL = { ...bC, align: 'left' };
    const eC = { fill: { color: '1A3A3A' }, color: '2AA198', fontSize: 7.5, bold: true, align: 'center', valign: 'middle' };
    const eL = { ...eC, align: 'left' };
    s5.addTable([
      [{ text: 'Method', options: bH }, { text: 'Paper', options: bH }, { text: 'Venue', options: bH }, { text: 'Signal', options: bH }, { text: 'Direction', options: bH }, { text: 'Granularity', options: bH }, { text: 'Phase 1', options: bH }],
      [{ text: 'CaTS', options: bL }, { text: 'Calibrated Test-Time Scaling', options: bL }, { text: 'ICLR 26', options: bC }, { text: 'Platt confidence', options: bL }, { text: 'Fixed', options: bC }, { text: 'Problem', options: bC }, { text: 'Yes (200ep)', options: bC }],
      [{ text: 'SEAG', options: bL }, { text: 'Semantic Exploration w/ Adaptive Gating', options: bL }, { text: 'ACL 25', options: bC }, { text: 'Mean token conf.', options: bL }, { text: 'Fixed', options: bC }, { text: 'Problem', options: bC }, { text: 'Yes (200ep)', options: bC }],
      [{ text: 'CoRefine', options: bL }, { text: 'Confidence-Guided Self-Refinement', options: bL }, { text: 'arXiv 26', options: bC }, { text: 'Per-token entropy', options: bL }, { text: 'Fixed', options: bC }, { text: 'Problem', options: bC }, { text: 'Yes (200ep)', options: bC }],
      [{ text: 'CATTS', options: bL }, { text: 'Agentic Test-Time Scaling for WebAgents', options: bL }, { text: 'arXiv 26', options: bC }, { text: 'Vote entropy+margin', options: bL }, { text: 'Fixed', options: bC }, { text: 'Problem', options: bC }, { text: 'No (K\u00D7fwd)', options: bC }],
      [{ text: 'AUQ', options: bL }, { text: 'Agentic Uncertainty Quantification', options: bL }, { text: 'arXiv 26', options: bC }, { text: 'Confidence', options: bL }, { text: 'Fixed', options: bC }, { text: 'Problem', options: bC }, { text: 'Yes', options: bC }],
      [{ text: 's1_budget', options: bL }, { text: 's1: Simple Test-Time Scaling', options: bL }, { text: 'EMNLP 25', options: bC }, { text: 'Fixed budget', options: bL }, { text: '\u2014', options: bC }, { text: 'Problem', options: bC }, { text: 'No', options: bC }],
      [{ text: 'EAAG (ours)', options: eL }, { text: 'Environment-Aware Adaptive Gating', options: eL }, { text: '\u2014', options: eC }, { text: 'Multi (auto)', options: eL }, { text: 'Learned', options: eC }, { text: 'Step', options: eC }, { text: 'No', options: eC }],
    ], { ...bt, border: { pt: 0.5, color: '3A4A5E' }, colW: [0.8, 2.2, 0.7, 1.2, 0.7, 0.75, 0.9], rowH: [0.28, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.28], autoPage: false });
  }

  // Slide 6: Combined SR/Cost — ALL 6 environments (updated costs from new CSV)
  const { slide: s6, placeholders: p6 } = await html2pptx(path.join(DIR, 'slide06_results.html'), pptx);
  const ft = p6.find(p => p.id === 'full-table');
  if (ft) {
    s6.addTable([
      [{ text: 'Method', options: H }, { text: 'HotpotQA', options: H }, { text: 'APPS Intro', options: H }, { text: 'WebShop', options: H }, { text: 'FEVER', options: H }, { text: 'TWExpress', options: H }, { text: 'Plancraft', options: H }],
      [{ text: 'base_only', options: CL },     c('49.0','0.00'), c('58.5','0.00'), c('7.2','0.00'),   c('37.0','0.00'),  c('67.5','0.00'),  c('29.8','0.00')],
      [{ text: 'always_trigger', options: CL }, c('97.0','1.80'), c('64.5','2.58'), c('43.0','5.63'),  c('99.8','1.46'),  c('99.3','3.45'),  c('22.8','6.99')],
      [{ text: 'CaTS*', options: CL },          c('93.2','1.06'), c('59.0','0.04'), c('30.5','3.05'),  c('50.2','4.71'),  c('96.7','1.97'),  c('22.3','4.39',R)],
      [{ text: 'SEAG*', options: CL },           c('67.5','0.80'), c('58.5','0.01'), c('28.0','2.28'),  c('49.3','3.12'),  c('97.3','2.30'),  c('24.8','2.16')],
      [{ text: 'CoRefine*', options: CL },       c('68.2','0.79'), c('58.5','0.01'), c('27.5','2.21'),  c('49.8','3.12'),  c('97.5','2.26'),  c('22.8','2.06')],
      [{ text: 'CATTS', options: CL },            c('68.3','1.07'), c('58.5','0.03'), c('16.0','0.19'), c('34.2','0.06',R),c('97.5','2.26'),  c('25.0','2.14')],
      [{ text: 'AUQ', options: CL },              c('97.0','1.69'), c('61.3','1.73'), c('35.7','5.33'), c('40.7','1.17'),  c('95.5','1.24'),  c('24.2','6.78')],
      [{ text: 's1_budget', options: CL },        c('97.0','1.04'), c('63.7','1.00'), c('7.8','1.00'),  c('46.2','1.58'),  c('95.0','1.09'),  c('18.3','1.68',R)],
      [{ text: 'EAAG', options: EL },             c('95.2','1.34',E),c('66.0','1.20',E),c('43.8','2.29',E),c('49.8','2.99',E),c('99.0','2.84',E),c('23.3','3.69',E)],
    ], { ...ft, border: { pt: 0.5, color: '3A4A5E' }, colW: [0.95, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1], rowH: [0.3].concat(Array(9).fill(0.28)), autoPage: false });
  }

  // Slide 7: Head-to-Head (updated costs)
  await html2pptx(path.join(DIR, 'slide08_h2h.html'), pptx);

  // Slide 8: Storyline
  await html2pptx(path.join(DIR, 'slide09_storyline.html'), pptx);

  // Slide 9: Paper Structure
  await html2pptx(path.join(DIR, 'slide10_structure.html'), pptx);

  const outPath = path.join(DIR, '..', 'week_report_2026-03-23.pptx');
  await pptx.writeFile({ fileName: outPath });
  console.log('Created: ' + outPath);
}

build().catch(e => { console.error(e); process.exit(1); });
