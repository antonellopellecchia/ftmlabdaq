## Installation and first configuration

After cloning the repository and moving to the `ftmlabdaq` folder,
```bash
source env.sh
poetry install -vv
```

## Usage

```bash
source env.sh
poetry shell
ftm --help
```

## To be included

- Add Keysight femtoammeter support
- Support gain measurement and analysis
- Saving signals from RTO scopes
- Saving signals on scope, then moving automatically to DAQ machine to increase rate
- Merge and integrate with waveform analysis repository

