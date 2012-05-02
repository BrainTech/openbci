function default(varargin)
%DEFAULT: set missing or empty variables or structure fields to given value
%
% default(name, value)
% default(name, func_handle, [args ...])
%  name is a string referring to a variable in the workspace of the caller.
%  If the named variable is not defined or is empty, it is defaulted to
%  value or the return-value of func_handle called with optional arguments.
%  If the named variable is defined & non-empty, func_handle is not called.
%
% default(strc, field, value)
% default(strc, field, func_handle, [args ...])
%  strc is a structure (though not a struct array, or part of one, since it
%  must be simply named, according to inputname from inside DEFAULT), and
%  field is a string containing a field-name.
%  If strc.(field) is missing or empty, it is defaulted as above.
%
% Examples:
%  clear tolerance, default('tolerance', eps) % (tolerance == eps)
%  verbose = true; default('verbose', false); % (verbose remains true)
%
%  default('options', struct), default(options, 'tolerance', eps) % etc.
%
%  default('direc', @uigetdir, '', 'Select output directory')
%
% Note: the reason for the function handle format here, instead of e.g.
%  default('direc', uigetdir('', 'Select output directory'))
% is that the function is only called if the file variable is missing or
% empty; if it is already set, the (unwanted) user-interface is not opened.
% Also note that default('example', @randn, 1e4) is hence much more
% efficient than default('example', randn(1e4)) if example is already set.
% 
% This is useful in functions with named optional arguments, for example:
%    function out = dosomething(in, tolerance, verbose)
%    default('tolerance', eps), default('verbose', false)
%    if verbose, display('Doing something...'), end
%    out = doit(in, tolerance);
% Not only is this more concise than using nargin, etc., but also if the
% function is later redefined - e.g. to add other intermediate options:
%    function out = dosomething(in, method, options, tolerance, verbose)
% then the existing code does not need changing, whereas any references to
% nargin would need updated numbers -- a tedious and bug-prone procedure.
% Another advantage of using DEFAULT is that it can be used at the MATLAB
% command prompt (and hence easily tested, e.g. using "evaluate selection"
% (F9) in the MATLAB editor) while nargin only works in running functions.
%
% See also: nargchk, nargin, varargin, inputname, mfilename

% Copyright (c) 2009, Ged Ridgway
% All rights reserved.
% 
% Redistribution and use in source and binary forms, with or without 
% modification, are permitted provided that the following conditions are 
% met:
% 
%     * Redistributions of source code must retain the above copyright 
%       notice, this list of conditions and the following disclaimer.
%     * Redistributions in binary form must reproduce the above copyright 
%       notice, this list of conditions and the following disclaimer in 
%       the documentation and/or other materials provided with the distribution
%       
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
% AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
% IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
% ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
% LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
% CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
% SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
% INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
% CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
% ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
% POSSIBILITY OF SUCH DAMAGE.

error(nargchk(2, inf, nargin, 'struct'));

if ischar(varargin{1})
    arg = varargin{1};
    if evalin('caller', ['~exist(''' arg ''', ''var'') || isempty(' arg ')'])
        val = varargin{2};
        if isa(val, 'function_handle')
            val = val(varargin{3:nargin});
            % (note nargin can be 2, in which case val() is called)
        else % if not function, can't have more than two input arguments:
            error(nargchk(2, 2, nargin, 'struct'));
        end
        assignin('caller', arg, val);
        % Note this might seem inefficient for large objects, but MATLAB
        % uses copy-on-write, so no unnecessary copies of val are made.
    end
elseif isstruct(varargin{1})
    error(nargchk(3, inf, nargin, 'struct')); % require strc, field and val
    if isempty(inputname(1))
        error('Structure argument is unnamed - see ''help default''')
    end
    [strc field val] = varargin{:};
    if isa(val, 'function_handle')
        val = val(varargin{4:nargin});
        % (note nargin can be 3, in which case val() is called)
    else % if not function, can't have more than three input arguments:
        error(nargchk(3, 3, nargin, 'struct'));
    end
    if ~isfield(strc, field) || isempty(strc.(field))
        strc.(field) = val;
        % It appears that the new field might require an entire copy...
    end
    assignin('caller', inputname(1), strc) % ...and that this would...
    % surprisingly though, it appears MATLAB's copy-on-write is clever
    % enough to avoid both these copies. Contrast this slow copy:
    %   test.data = randn(1e4); % A large array
    %   copy = test;            % A fast copy-by-reference
    %   copy.data(1) = 1;       % A slow copy-on-write
    % with the following very fast modification:
    %   default(test, 'flag', true), display(test)
else
    error('Invalidate input - see ''help default''')
end