Indra and Vali
==============

Indra is a cross-platform, Python-based program to create synthetic
weather time series from a weather record of at least one year. Vali is
the child of Indra created for use with ESP-r on 31 May 2018
(*v2.78\_esru*).

See the [*wiki*](https://github.com/paragrastogi/SyntheticWeather/wiki)
if you want to find out more about **indra**. It contains a step-by-step
guide to installing and running mighty **indra**. If you know your way
around, go directly to the sample commands below.

**Indra is NOT a weather forecasting tool.** It is designed to be used
to create variations on weather patterns learned from a source file.

You can call **indra** using the python and shell scripts called vali.py
and vali.sh respectively (they are the same script, just written in the
two different languages).

Indra and Vali only work with Python 3.5+. They might work with older
versions of Python but certainly not before v3. They have been tested on
Windows 10 and Ubuntu 16.04. They will probably work on MacOs as well,
since the commands are related to Python and not the OS. The most common
error you will encounter, especially in Unix-based systems, is that your
default Python install is Python 2. In this case, simply replace all
calls to python (in Vali and below) to python3. That is, you will have
to explicitly call Python 3+.

Bibliography
------------

The program is based on the algorithms published in Rastogi (2016),
Rastogi and Andersen (2015, 2016).\

-   Full wiki for Indra:
    https://github.com/paragrastogi/SyntheticWeather/wiki
-   Rastogi, Parag. 2016. On the Sensitivity of Buildings to Climate:
    The Interaction of Weather and Building Envelopes in Determining
    Future Building Energy Consumption. PhD, Lausanne, Switzerland:
    Ecole polytechnique federale de Lausanne. EPFL Infoscience.
    https://infoscience.epfl.ch/record/220971?ln=en.
-   Rastogi, Parag, and Marilyne Andersen. 2015. Embedding Stochasticity
    in Building Simulation Through Synthetic Weather Files. In
    Proceedings of BS 2015. Hyderabad, India.
    http://infoscience.epfl.ch/record/208743.
-   Rastogi, Parag, and Marilyne Andersen. 2016. Incorporating Climate
    Change Predictions in the Analysis of Weather-Based Uncertainty. In
    Proceedings of SimBuild 2016. Salt Lake City, UT, USA.
    http://infoscience.epfl.ch/record/208743.

@phdthesis{rastogi\_sensitivity\_2016, address = {Lausanne,
Switzerland}, type = {{PhD}}, title = {On the sensitivity of buildings
to climate: the interaction of weather and building envelopes in
determining future building energy consumption}, shorttitle =
{Sensitivity of {Buildings} to {Climate}}, url =
{https://infoscience.epfl.ch/record/220971?ln=en}, language = {EN},
school = {Ecole polytechnique federale de Lausanne}, author = {Rastogi,
Parag}, month = aug, year = {2016}, note =
{doi:10.5075/epfl-thesis-6881} }\

License, implementation, and compatibility
------------------------------------------

This tool is distributed under the GNU General Public License v3
(GPLv3). Please read what this means
[here](https://en.wikipedia.org/wiki/GNU_General_Public_License). These
scripts come with absolutely no warranties/guarantees of any kind. Happy
creating fake weather!

Sample Commands
---------------

If you type python indra.py --help into the command line, you will see
how to use the commands. Some sample customisations are given below:

### Change ARMA parameters and bounds

#### Windows


        python indra.py --train 1 --station_code gen --n_samples 10 --path_file_in gen\gen_iwec.epw --path_file_out gen\gen_iwec_syn.epw --file_type epw --store_path gen --arma_params [2,2,0,0,0] --bounds [1,99]

#### Unix


        python indra.py --train 1 --station_code 'gen' --n_samples 10 --path_file_in 'gen/gen_iwec.epw' --path_file_out 'gen/gen_iwec_syn.epw' --file_type 'epw' --store_path 'gen' --arma_params '[2,2,0,0,0]' --bounds '[1,99]'

### Change number of samples requested

#### Windows


        python indra.py --train 1 --station_code gen --n_samples 100 --path_file_in gen\gen_iwec.epw --path_file_out gen\gen_iwec_syn.epw --file_type epw --store_path gen

#### Unix


        python indra.py --train 1 --station_code 'gen' --n_samples 100 --path_file_in 'gen/gen_iwec.epw' --path_file_out 'gen/gen_iwec_syn.epw' --file_type 'epw' --store_path 'gen'
