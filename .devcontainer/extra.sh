packages_to_install() {
    echo -n "g++-9,libclang-dev,libgl1-mesa-dev,libxkbcommon-x11-0,libdbus-1-3,libpulse-mainloop-glib0"
    
    case $QT in 
        5*)
            echo -n ",libpulse-mainloop-glib0"
        ;;
        *)
            echo ""
        ;;
    esac
}