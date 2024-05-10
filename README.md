# Personal assistant

## go to the main directory
```bash
    cd personal_assistant
```

## Install dependencies
```bash
    source venv/bin/activate
    pip install -r requirements.txt
```

## Run demo scripts
```bash
    python -m solve_recapcha_demo
    python -m solve_slide_capcha_demo
    python -m docstudio_sign_demo
    
    python -m uefa.uefa_service
```

## TODO:
* use proxy server for reCapcha
* Calculate the requests limit per hour to get the maximum chance of passing the reCapcha



