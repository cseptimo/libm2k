%
% Copyright (c) 2024 Analog Devices Inc.
%
% This file is part of libm2k
% (see http://www.github.com/analogdevicesinc/libm2k).
%
% This program is free software; you can redistribute it and/or modify
% it under the terms of the GNU Lesser General Public License as published by
% the Free Software Foundation, either version 2.1 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU Lesser General Public License for more details.
%
% You should have received a copy of the GNU Lesser General Public License
% along with this program. If not, see <http://www.gnu.org/licenses/>.
%

clear all; % clc;

%% MATLAB API Builder
% This script will build the basic template file for the MATLAB bindings
% however since the library processor isn't perfect manual modifications
% need to be done with the generated interface file

includepath = fullfile(pwd, 'libm2k', 'include');
hppPath = fullfile(pwd, 'libm2k', 'include', 'libm2k');

%%
% check if we have an unix based system but not macos
if isunix && not(ismac)
    % Full path to files in the library
    libs = fullfile(pwd, 'libm2k', 'libm2k.so');
    myPkg = 'libm2k';

elseif ismac
    % on mac pc we need to specify the compiler 
    mex -setup C++
    libs = fullfile(pwd, 'libm2k', 'libm2k.dylib');
    myPkg = 'libm2k';

elseif ispc
    % on windows pc we need to specify the compiler 
    mex -setup C++ -v
    % Full path to files in the library
    libs = fullfile(pwd, 'libm2k', 'libm2k.lib');
    myPkg = 'libm2k';

else
    error('Build did not find any recognized system');
end

%% Add related headers
h = {};

h1 = fullfile(hppPath, 'digital', 'm2kdigital.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'digital', 'enums.hpp'); h = [{h1}, h(:)'];

h1 = fullfile(hppPath, 'analog', 'm2kanalogout.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'analog', 'm2kanalogin.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'analog', 'm2kpowersupply.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'analog', 'dmm.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'analog', 'enums.hpp'); h = [{h1}, h(:)'];

h1 = fullfile(hppPath, 'utils', 'utils.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'utils', 'enums.hpp'); h = [{h1}, h(:)'];

h1 = fullfile(hppPath, 'm2khardwaretrigger.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'contextbuilder.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'm2k.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'm2kglobal.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'context.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'logger.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'm2kcalibration.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'm2kexceptions.hpp'); h = [{h1}, h(:)'];
h1 = fullfile(hppPath, 'enums.hpp'); h = [{h1}, h(:)'];
headers = h;

%% Build interface file
% delete definelibm2k.m

if isunix && not(ismac)
    clibgen.generateLibraryDefinition(headers, ...
        'IncludePath', includepath, ...
        'Libraries', libs, ...
        'PackageName', myPkg, ...
        'Verbose', true)
    delete definelibm2k.mlx

elseif ismac
    %% Add 'DefinedMacros' to fix bugs related to compiler versions used by matlab 
    clibgen.generateLibraryDefinition(headers, ...
        'IncludePath', includepath, ...
        'Libraries', libs, ...
        'InterfaceName', myPkg, ...
        'Verbose', true, ...
        'DefinedMacros', ["_HAS_CONDITIONAL_EXPLICIT=0", "_USE_EXTENDED_LOCALES_"])
    delete definelibm2k.mlx

elseif ispc
    %% Add 'DefinedMacros' to fix builds using Visual Studio 16 2019
    clibgen.generateLibraryDefinition(headers, ...
        'IncludePath', includepath, ...
        'Libraries', libs, ...
        'PackageName', myPkg, ...
        'Verbose', true, ...
        'DefinedMacros', ["_HAS_CONDITIONAL_EXPLICIT=0"])
    delete definelibm2k.mlx
end

if isunix && not(ismac)
    pkg = definelibm2k_linux64;

elseif ismac
    if strcmp(computer('arch'), 'maca64')
        pkg = definelibm2k_macM1;
    else
        pkg = definelibm2k_mac86;
    end

elseif ispc
    pkg = definelibm2k_win64;
end

%% Build library once manually updated
% build(pkg);
