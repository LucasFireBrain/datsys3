DATSYS3/
│
├── CliApp/
│   ├── datsys.py          # CLI entrypoint + menu
│   ├── projects.py        # project creation & discovery
│
├── clients/
│   ├── clients.py         # client logic
│   └── PSO/               # example client
│       ├── client.json
│       └── QXXX-PSO-PK6/
│           ├── peekCase.json
│           ├── Log.txt
│           ├── DICOM/
│           ├── Blender/
│           └── 3DSlicer/
│
├── peek/
│   ├── peek.py                    # terminal PEEK logic
│   └── peek_blender_macros/       # Blender-only scripts
│       ├── autoFat.py
│       ├── caseTools.py
│       ├── idBridge.py
│       ├── snapshotCameras.py
│       └── versionControl.py
│
├── templates/
│   └── PK/
│       ├── 3DSlicer/
│       │   └── Segmentations/
│       ├── Blender/
│       │   └── PEEK.blend
│       ├── DICOM/
│       ├── Log.txt
│       └── peekCase.json
│
├── utils/
│   └── utils.py            # base36, dates, helpers
│
├── docs/
│   ├── architecture.md     # system contract
│   └── readme.md
│
└── hospitals.csv
