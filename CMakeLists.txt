cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

if(POLICY CMP0068)
  cmake_policy(SET CMP0068 NEW)
endif()

project(LimeReport6)

set(USE_QT6 ON)
find_package(QT REQUIRED NAMES Qt6)
find_package(
  Qt${QT_VERSION_MAJOR}
  COMPONENTS Core Widgets Sql Network Xml Svg Qml PrintSupport REQUIRED
)
# find_package(PythonLibs REQUIRED)
find_package(Shiboken6 REQUIRED)
find_package(PySide6 REQUIRED)


get_target_property(LIBSHIBOKEN_INCLUDE_DIRS Shiboken6::libshiboken INTERFACE_INCLUDE_DIRECTORIES)
get_target_property(PYSIDE_INCLUDE_DIRS PySide6::pyside6 INTERFACE_INCLUDE_DIRECTORIES)
# find_package(PySide6 REQUIRED)

add_subdirectory(LimeReport)

set(CMAKE_CXX_STANDARD 17)

set(wrapped_header ${CMAKE_SOURCE_DIR}/bindings.h)
set(typesystem_file ${CMAKE_SOURCE_DIR}/bindings.xml)

set(generated_sources
  limereport_idatasourceholder_wrapper.cpp
  limereport6_module_wrapper.cpp
  limereport_icallbackdatasource_wrapper.cpp
  limereport_enums_wrapper.cpp
  limereport_idbcredentialsprovider_wrapper.cpp
  limereport_reportengine_wrapper.cpp
  limereport_idatasource_wrapper.cpp
  limereport_idatasourcemanager_wrapper.cpp
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
  /usr/share/PySide6/typesystems
)
list(REMOVE_DUPLICATES SHIBOKEN_TYPESYSTEMS)
list(TRANSFORM SHIBOKEN_TYPESYSTEMS PREPEND "-T")

# Qt6PrintSupport_DEFINITIONS
# ===============

set(shiboken_generator_path "/usr/bin")

set(shiboken_path "${shiboken_generator_path}/shiboken6${CMAKE_EXECUTABLE_SUFFIX}")
if(NOT EXISTS ${shiboken_path})
  message(FATAL_ERROR "Shiboken executable not found at path: ${shiboken_path}")
endif()

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
  Shiboken6::libshiboken
  PySide6::pyside6
)

target_include_directories(${PROJECT_NAME} PRIVATE ${PYTHON_INCLUDE_DIRS})
target_include_directories(${PROJECT_NAME} PRIVATE ${LIBSHIBOKEN_INCLUDE_DIRS})

foreach(_dir IN LISTS PYSIDE_INCLUDE_DIRS)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir})
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtCore)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtGui)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtWidgets)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtQml)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtNetwork)
  target_include_directories(${PROJECT_NAME} PRIVATE ${_dir}/QtPrintSupport)
endforeach()
