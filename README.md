docker run -it --rm -p 5000:5000 -e TEST1="1000" -e DISPLAY=192.168.1.45:0.0 -v "C:/Users/Utilisateur/Documents/coursMA1/MIR:/opt/TP" nayruiv/monimage:latest

docker run -it --rm -p 5000:5000 -e TEST1="1000" -e DISPLAY=192.168.56.1:0.0 -v "C:/Users/Utilisateur/Documents/coursMA1/MIR:/opt/TP" nayruiv/monimage:latest
