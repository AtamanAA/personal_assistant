# Personal assistant

## go to the main directory
```bash
    cd personal_assistant
```

## Install dependencies
```bash
    source venv/bin/activate
    pip install -r requirements.txt
    

#    apt install ffmpeg -y
```

## Install google chrome
```bash
    sudo apt install fonts-liberation libu2f-udev libvulkan1
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb    
    sudo dpkg -i google-chrome-stable_current_amd64.deb

```

### Available commands for user assistant
```bash
systemctl restart personal_assistant
systemctl stop personal_assistant
systemctl start personal_assistant
systemctl status personal_assistant
```

## Run demo scripts
```bash
    python -m services.uefa.uefa_service
    python -m services.real_madrid.real_madrid_service

#    python -m solve_recapcha_demo
#    python -m solve_slide_capcha_demo
#    python -m docstudio_sign_demo
#    python -m cloud_capcha_demo
```

## API
```bash
  uvicorn main:app --host 0.0.0.0 --port 8004
```

## TODO:
* use proxy server for reCapcha
* Calculate the requests limit per hour to get the maximum chance of passing the reCapcha



