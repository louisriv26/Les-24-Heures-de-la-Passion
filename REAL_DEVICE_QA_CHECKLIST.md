# Real-device QA checklist — v101.142 R1

Use only the exact externally SHA-bound v101.142 R1 candidate. Internal browser evidence does not substitute for physical-device/PWA/accessibility gates.

## Native visible-flow topology
- Hour 14: confirm the final segment of P008 flows directly into P009→P010→P011 with no artificial visible paragraph gap, while P008 segments 1–2 retain their internal paragraph rhythm and a true break remains before P012.
- Hour 18: confirm P055→P056 and P062→P063 flow inline with no artificial gap; confirm the true break before P064 remains. Do not expect newly created bullets/list styling.
- Hour 22: confirm P019→P020 flows inline with no artificial gap. Do not expect newly created bullets/list styling.
- Verify existing five inherited continuity pairs remain unchanged.

## Protected regression
- Search titles/direct-speech/result totals/deep links remain identical to v101.141 R1 behavior.
- Notes, highlights, copy/selection, Samsung whole-visible-paragraph mode, last-place/resume, progression, theme and font settings continue to resolve through the unchanged stable paragraph IDs.
- Existing Hour 24 and Méditée behavior remains intact.

## External gates
- Physical iPhone validation.
- Physical iPad portrait and landscape validation.
- Physical Samsung/Android validation.
- Live-origin exact-byte binding.
- Installed-PWA update and three close/reopen cycles.
- True offline cold reopen.
- Representative VoiceOver and TalkBack navigation.

Final public deployment remains unauthorized until all external gates are evidenced.
