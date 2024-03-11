cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

if(POLICY CMP0068)
  cmake_policy(SET CMP0068 NEW)
endif()

project(LimeReport)

# LimeReport options
set(USE_QT6 ON)
if (NOT DEFINED ENABLE_ZINT)
  set(ENABLE_ZINT OFF)
endif()
#
set(LIMEREPORT_STATIC ON)

message(ENABLE_ZINT, ${ENABLE_ZINT})

# Find Python
find_package (Python3 COMPONENTS Interpreter)
if(NOT Python3_Interpreter_FOUND)
    message(FATAL_ERROR "Python3 not found")
endif()
message(STATUS "Using python: ${Python3_EXECUTABLE}")


if (NOT DEFINED PYSIDE_INSTALL_DIR)
    set(PYSIDE_INSTALL_DIR $ENV{PYSIDE_INSTALL_DIR})
endif()

list(APPEND CMAKE_PREFIX_PATH ${PYSIDE_INSTALL_DIR})

find_package(QT REQUIRED NAMES Qt6)
find_package(
  Qt${QT_VERSION_MAJOR}
  COMPONENTS Core Widgets Sql Network Xml Svg Qml PrintSupport REQUIRED
)

# Macro to get various pyside / python include / link flags and paths.
# Uses the not entirely supported utils/pyside_config.py file.
macro(pyside_config option output_var)
    if(${ARGC} GREATER 2)
        set(is_list ${ARGV2})
    else()
        set(is_list "")
    endif()

    execute_process(
      COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/pyside_config.py"
              ${option}
      OUTPUT_VARIABLE ${output_var}
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if ("${${output_var}}" STREQUAL "")
        message(FATAL_ERROR "Error: Calling ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/pyside_config.py ${option} returned no output.")
    endif()
    if(is_list)
        string (REPLACE " " ";" ${output_var} "${${output_var}}")
    endif()
endmacro()

# Query for the shiboken generator path, Python path, include paths and linker flags.
pyside_config(--shiboken-module-path shiboken_module_path)
pyside_config(--shiboken-generator-path shiboken_generator_path)
pyside_config(--pyside-path pyside_path)
pyside_config(--pyside-include-path pyside_include_dir 1)
pyside_config(--python-include-path python_include_dir)
pyside_config(--shiboken-generator-include-path shiboken_include_dir 1)
pyside_config(--shiboken-module-shared-libraries-cmake shiboken_shared_libraries 0)
pyside_config(--python-link-flags-cmake python_linking_data 0)
pyside_config(--pyside-shared-libraries-cmake pyside_shared_libraries 0)

set(shiboken_path "${shiboken_generator_path}/shiboken6${CMAKE_EXECUTABLE_SUFFIX}")
if(NOT EXISTS ${shiboken_path})
    message(FATAL_ERROR "Shiboken executable not found at path: ${shiboken_path}")
endif()

add_subdirectory(LimeReport)

set(CMAKE_CXX_STANDARD 11)

set(wrapped_header ${CMAKE_SOURCE_DIR}/bindings.h)
set(typesystem_file ${CMAKE_SOURCE_DIR}/bindings.xml)

set(generated_sources
  limereport_module_wrapper.cpp
  limereport_enums_wrapper.cpp
  limereport_reportengine_wrapper.cpp
  limereport_icallbackdatasource_wrapper.cpp
  limereport_idatasource_wrapper.cpp
  limereport_idatasourceholder_wrapper.cpp
  limereport_idatasourcemanager_wrapper.cpp
  limereport_idbcredentialsprovider_wrapper.cpp
)

list(TRANSFORM generated_sources PREPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}/)

set(SHIBOKEN_INCLUDES
  ${CMAKE_SOURCE_DIR}
  ${CMAKE_SOURCE_DIR}/LimeReport/include
  ${Qt6Core_INCLUDE_DIRS} 
  ${Qt6Widgets_INCLUDE_DIRS} 
  ${Qt6Qml_INCLUDE_DIRS} 
  ${Qt6PrintSupport_INCLUDE_DIRS}
)
list(REMOVE_DUPLICATES SHIBOKEN_INCLUDES)
list(TRANSFORM SHIBOKEN_INCLUDES PREPEND "-I")

set(SHIBOKEN_TYPESYSTEMS
  ${CMAKE_SOURCE_DIR}
  ${pyside_path}/typesystems
)
list(REMOVE_DUPLICATES SHIBOKEN_TYPESYSTEMS)
list(TRANSFORM SHIBOKEN_TYPESYSTEMS PREPEND "-T")


set(shiboken_options 
  --generator-set=shiboken 
  --enable-parent-ctor-heuristic
  --enable-return-value-heuristic 
  --use-isnull-as-nb_nonzero 
  --enable-pyside-extensions 
  --avoid-protected-hack
  ${SHIBOKEN_INCLUDES}
  ${SHIBOKEN_TYPESYSTEMS}
  --output-directory=${CMAKE_CURRENT_BINARY_DIR}
)

set(generated_sources_dependencies ${wrapped_header} ${typesystem_file})

add_custom_command(OUTPUT ${generated_sources}
                    COMMAND ${shiboken_path}
                    ${shiboken_options} ${wrapped_header} ${typesystem_file}
                    DEPENDS ${generated_sources_dependencies}
                    IMPLICIT_DEPENDS CXX ${wrapped_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${typesystem_file}.")

# ===============

set(${PROJECT_NAME}_sources ${generated_sources})

add_library(${PROJECT_NAME} MODULE ${${PROJECT_NAME}_sources})
set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "")

target_link_libraries(${PROJECT_NAME} 
  limereport-qt${QT_VERSION_MAJOR} 
)

target_link_libraries(${PROJECT_NAME} 
  ${LIBSHIBOKEN_LIBRARY}
  ${pyside_shared_libraries}
)

target_include_directories(${PROJECT_NAME} PRIVATE ${python_include_dir})
target_include_directories(${PROJECT_NAME} PRIVATE ${shiboken_include_dir})

foreach(_dir IN LISTS pyside_include_dir)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir})
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtCore)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtGui)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtWidgets)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtQml)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtNetwork)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtPrintSupport)
endforeach()

set_target_properties(${PROJECT_NAME} PROPERTIES BUILD_RPATH "$ORIGIN/PySide6/:$ORIGIN/shiboken6/:$ORIGIN/PySide6/:$ORIGIN/PySide6/Qt/lib/:$ORIGIN/")

if(WIN32)
    set_property(TARGET ${PROJECT_NAME} PROPERTY SUFFIX ".pyd")
endif()

if(APPLE)
  set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "-undefined dynamic_lookup")
endif(APPLE)

if (WIN32)
    list(GET python_linking_data 0 python_libdir)
    target_link_libraries(${PROJECT_NAME} PRIVATE ${python_libdir})
endif()

# ===============

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                    COMMAND ${PYTHON_EXECUTABLE}
                    ${CMAKE_SOURCE_DIR}/build_scripts/pyi_generator.py
                    $<TARGET_FILE:${PROJECT_NAME}>
                    COMMENT "Running pyi_generator")