#!/bin/bash

# Custom aliases for container internal user's shell

alias zshconfig="code ~/.zshrc"
alias ohmyzsh="code ~/.oh-my-zsh"
alias p10k="code ~/.p10k.zsh"
alias update="sudo apt-get update && sudo apt full-upgrade -y"
alias ls="lsd --group-dirs=first -S"
alias ll="ls -l --total-size -h"
alias la="ll -a"
alias lt="ls --tree --depth=1 "
alias clc='clear'
alias py2='source ~/venvs/py27/bin/activate'
alias py3='source ~/venvs/py310/bin/activate'
alias pip='python -m pip'
alias cm='cd ~/catkin_ws && catkin_make && source devel/setup.zsh'
alias pippo='roslaunch pepper_bringup pepper_full_py.launch nao_ip:=10.1.1.140 roscore_ip:=localhost'
alias pippa='roslaunch pepper_bringup pepper_full_py.launch nao_ip:=10.1.1.2 roscore_ip:=localhost'
alias movebot='rosrun rqt_robot_steering rqt_robot_steering'
alias movejoint='rosrun rqt_joint_trajectory_controller rqt_joint_trajectory_controller'
alias cb='cd ~/catkin_ws && catkin build -j5 --summarize && source devel/setup.zsh'
alias rviz='rosrun rviz rviz -d ~/workspace/src/rviz_config/pepper.rviz'