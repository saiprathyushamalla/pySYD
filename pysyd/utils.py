import os
import ast
import glob
import numpy as np
import pandas as pd
from astropy.io import ascii
import multiprocessing as mp
from astropy.stats import mad_std
from scipy.signal import find_peaks



# Package mode
from . import models
from . import SYDFILE, PYSYDFILE
from . import INFDIR, INPDIR, OUTDIR


class PySYDInputError(Exception):
    """Class for pySYD user input errors."""
    def __repr__(self):
        return "PySYDInputError"
    __str__ = __repr__

class PySYDProcessingError(Exception):
    """Class for pySYD processing exceptions."""
    def __repr__(self):
        return "PySYDProcessingError"
    __str__ = __repr__

class PySYDInputWarning(Warning):
    """Class for pySYD user input warnnings."""
    def __repr__(self):
        return "PySYDInputWarning"
    __str__ = __repr__


class Constants:
    """
    
    Container class for constants and known values -- which is
    primarily solar asteroseismic values for our purposes.
    
    """

    def __init__(self, defaults=['solar','conversions','constants']):
        """
        UNITS ARE IN THE SUPERIOR CGS 
        COME AT ME

        """
        self.constants = {}
        params = dict(
            m_sun = 1.9891e33,
            r_sun = 6.95508e10,
            rho_sun = 1.41,
            teff_sun = 5777.0,
            logg_sun = 4.4,
            teffred_sun = 8907.0,
            numax_sun = 3090.0,
            dnu_sun = 135.1,
            width_sun = 1300.0,
            tau_sun = [5.2e6,1.8e5,1.7e4,2.5e3,280.0,80.0],
            tau_sun_single = [3.8e6,2.5e5,1.5e5,1.0e5,230.,70.],
            G = 6.67428e-8,
            cm2au = 6.68459e-14,
            au2cm = 1.496e+13,
            rad2deg = 180./np.pi,
            deg2rad = np.pi/180.,
        )
        self.constants.update(params)

    def __repr__(self):
        return "<Constants>"


class Parameters(Constants):
    """

    Container class for ``pySYD``

    """

    def __init__(self, args=None, stars=None):
        """

        Calls super method to inherit all relevant constants and then
        stores the default values for all pysyd modules

        Methods

        """
        # makes sure to inherit constants
        super().__init__()
        self.get_defaults()
        if not self._is_interactive():
            self._add_cli(args)
        else:
            if stars is None:
                self.star_list()
            else:
                self.params['stars'] = stars
        self.assign_stars()


    def __repr__(self):
        return "<PySYD Parameters>"


    def _is_interactive(self):
        import __main__ as main
        return not hasattr(main, '__file__')


    def get_defaults(self, params={}):
        """Load defaults

        Gets default pySYD parameters by calling functions analogous to the command-line 
        parsers 

        Attributes
            params : Dict[str[Dict[,]]]
                container class for ``pySYD`` parameters
    
        Calls
            - :mod:`pysyd.utils.Parameters.get_parent`
            - :mod:`pysyd.utils.Parameters.get_data`
            - :mod:`pysyd.utils.Parameters.get_main`
            - :mod:`pysyd.utils.Parameters.get_plot`

        """
        self.params = {}
        # Initialize high level functionality
        self.get_parent()
        # Get parameters related to data loading/saving
        self.get_data()
        # Initialize parameters for the estimate routine
        self.get_estimate()
        # Initialize parameters for the fit background routine
        self.get_background()
        # Initialize parameters relevant for estimating global parameters
        self.get_global()


    def get_parent(self, cli=False, inpdir='data', infdir='info', outdir='results', overwrite=False,  
                   show=False, ret=False, save=True, test=False, verbose=False,):
        """Get parent parser
   
        Load parameters available in the parent parser i.e. higher-level software functionality

        Parameters
            cli : bool, default=False
                this should not be touched - there is a function that determines this automatically
            inpdir : str, default=INPDIR
                path to input data 
            infdir : str, default=INFDIR
                path to star information 
            outdir : str, default=OUTDIR
                path to results 
            overwrite : bool, default=False
                allow files to be overwritten by new ones
            show : bool, default=False
                show output figures 
            ret : bool, default=False
                enable the returning of output in an interactive session
            save : bool, default=True
                save all data products
            test : bool, default=Ffalse
                test software functionality
            verbose : bool, default=False
                turn on verbose output

        Attributes
            params : Dict[str,Dict[,]]
                the updated parameters

        """
        high = dict(
            cli = cli,
            inpdir = INPDIR,
            infdir = INFDIR,
            outdir = OUTDIR,
            overwrite = overwrite,
            show = show,
            ret = ret,
            save = save,
            test = test,
            verbose = verbose,
        )
        self.params.update(high)


    def get_data(self, dnu=None, gap=20, info='star_info.csv', ignore=False, kep_corr=False, lower_ff=None, 
                 lower_lc=None, lower_ps=None, mode='load', notching=False, oversampling_factor=None, 
                 seed=None, stars=None, todo='todo.txt', upper_ff=None, upper_lc=None, upper_ps=None, 
                 stitch=False, n_threads=0,):
        """Get data parser
   
        Load parameters available in the data parser, which is mostly related to initial
        data loading and manipulation

        Parameters
            dnu : float, default=None
                spacing to fold PS in order to "whiten" mixed modes (**Note:** requires all 3 args)
            gap : int, default=20
                n times the number of cadences defines a "gap" (to correct for)
            info : str, default='info/star_info.csv'
                path to star csv info
            ignore : bool, default=False
                concise way to ignore inputs from star_info.csv
            kep_corr : bool, default=False
                use the module that corrects for known kepler artefacts
            lower_ff : float, default=None
                lower folded frequency limit to whiten mixed modes
            lower_lc : float, default=None
                lower limit for time series data
            lower_ps : float, default=None
                lower frequency limit of power spectrum
            mode : str, default='load'
                which `pySYD` mode to execute
            notching : bool, default=False
                option to use notching technique (vs. simulating white noise)
            oversampling_factor : int, default=None
                oversampling factor of input power spectrum
            seed : int, default=None
                save seed for reproducible results
            stars : List[str], default=None
                list of targets to process
            todo : str, default='info/todo.txt'
                path to star list to process
            upper_ff : float, default=None
                upper folded frequency limit to whiten mixed modes
            upper_lc : float, default=None
                upper limit for time series data
            upper_ps : float, default=None
                upper frequency limit of power spectrum
            stitch : bool, default=False
                use the module that corrects for large gaps in data
            n_threads : int
                number of threads to use when running in parallel mode

        Attributes
            params : Dict[str,Dict[,]]
                the updated parameters


        """
        data = dict(
            dnu = dnu,
            gap = gap,
            info = os.path.join(INFDIR, info),
            ignore = ignore,
            kep_corr = kep_corr,
            lower_ff = lower_ff,
            lower_lc = lower_lc,
            lower_ps = lower_ps,
            mode = mode,
            notching = notching,
            oversampling_factor = oversampling_factor,
            seed = seed,
            stars = stars,
            todo = os.path.join(INFDIR, todo),
            upper_ff = upper_ff,
            upper_lc = upper_lc,
            upper_ps = upper_ps,
            stitch = stitch,
            n_threads = n_threads,
        )
        self.params.update(data)


    def get_estimate(self, ask=False, binning=0.005, bin_mode='mean', estimate=True, adjust=False, 
                     lower_se=1.0, n_trials=3, smooth_width=10.0, step=0.25, upper_se=8000.0,):
        """Search and estimate parameters
    
        Get parameters relevant for the optional first module that looks for and identifies
        power excess due to solar-like oscillations and then estimates its properties 

        Parameters
            ask : bool, default=False
                If `True`, it will ask which trial to use as the estimate for numax
            binning : float, default=0.005
                logarithmic binning width
            bin_mode : {'mean', 'median', 'gaussian'}, default='mean'
                mode to use when binning
            estimate : bool, default=True
                disable the module that estimates numax
            adjust : bool, default=False
                adjusts default parameters based on numax estimate
            lower_se : float, default=1.0
                lower frequency limit of PS to use in the first module
            n_trials : int, default=3
                the number of trials to estimate :term:`numax`
            smooth_width: float, default=10.0
                box filter width (in :math:`\\rm \\mu Hz`) to smooth power spectrum
            step : float, default=0.25
                TODO: Write description
            upper_se : float, default=8000.0
                upper frequency limit of PS to use in the first module

        Attributes
            params : Dict[str,Dict[,]]
                the updated parameters

        """
        estimate = dict(
            ask = ask,
            binning = binning,
            bin_mode = bin_mode,
            estimate = estimate,
            adjust = adjust,
            lower_est = lower_est,
            n_trials = n_trials,
            smooth_width = smooth_width,
            step = step,
            upper_ex = upper_ex,
        )
        self.params.update(estimate)


    def get_background(self, background=True, basis='tau_sigma',  box_filter=1.0, ind_width=20.0, 
                       n_laws=None, lower_bg=1.0, metric='bic', models=False, n_rms=20, 
                       upper_bg=8000.0, fix_wn=False,):
        """Background parameters
    
        Gets parameters used during the automated background-fitting analysis 

        Parameters
            background : bool, default=True
                disable the background-fitting routine (not recommended)
            basis : str, default='tau_sigma'
                which basis to use for background fitting, e.g. {a,b} parametrization 
            box_filter : float, default=1.0
                the size of the 1D box smoothing filter (in :math:`\\rm \\mu Hz`)
            ind_width : float, default=20.0
                the independent average smoothing width (in :math:`\\rm \\mu Hz`)
            n_laws : int, default=None
                force number of Harvey-like components in background fit
            lower_bg : float, default=1.0
                lower frequency limit of PS to use for the background fit
            metric : str, default='bic'
                which metric to use (i.e. bic or aic) for model selection 
            models : bool, default=False
                include figure with the iterated bgmodel fits
            n_rms : int, default=20
                number of data points to estimate red noise contributions **Note:** this should never need to be changed
            upper_bg : float, default=8000.0
                upper frequency limit of PS to use for the background fit
            fix_wn : bool, default=False
                fix the white noise level in the background fit 
            functions : Dict[int:pysyd.models]
                pointer function to different models for the background fit

        Attributes
            params : Dict[str,Dict[,]]
                the updated parameters


        """
        background = dict(
            background = background,
            basis = basis,
            box_filter = box_filter,
            ind_width = ind_width,
            n_laws = n_laws,
            lower_bg = lower_bg,
            metric = metric,
            models = models,
            n_rms = n_rms,
            upper_bg = upper_bg,
            fix_wn = fix_wn,
            functions = get_dict(type='functions'),
        )
        self.params.update(background)


    def get_global(self, cmap='binary', clip_value=3.0, fft=True, globe=True, interp_ech=False, 
                   lower_osc=None, mc_iter=1, nox=None, noy='0+0', npb=10, numax=None, osc_width=1.0, 
                   n_peaks=10, smooth_ech=None, sm_par=None, smooth_ps=2.5, threshold=1.0, 
                   hey=False, upper_osc=None, samples=False,):
        """Global fitting parameters
    
        Get default parameters that are relevant for deriving global asteroseismic parameters 
        :math:`\\rm \\nu_{max}` and :math:`\\Delta\\nu`

        Parameters
            cmap : str, default='binary'
                change colormap of echelle diagram
            clip_value : float, default=3.0
                the minimum frequency of the echelle plot
            fft : bool, default=True
                if `True`, the ACF is computed using :term:`FFT`s 
            globe : bool, default=True
                disable the module that fits the global parameters 
            interp_ech : bool
                turns on the bilinear smoothing in echelle plot
            lower_osc : float, default=None
                lower frequency bound of the power spectrum used to calculate the :term:`ACF` 
            mc_iter : int, default=1
                number of samples used to estimate uncertainty
            nox : int, default=None
                x-axis resolution on the echelle diagram - default uses spacing and resolution to calculate appropriate number
            noy : str, default='0+0'
                how many radial orders to plot on the echelle diagram **NEW:** and how many orders to shift the ED by
            npb : int, default=10
                instead of specifying arbitrary value, provide how many frequencies should be in a given bin
            n_peaks : int, default=10
                the number of peaks to highlight in ACF and plot 
            numax : float, default=None
                provide initial value for numax to bypass the first module
            osc_width : float, default=1.0
                fractional width to use for power excess centered on :term:`numax`
            smooth_ech : float, default=None
                option to smooth the output of the echelle plot
            sm_par : float, default=None
                Gaussian filter width for determining smoothed numax (values are typically between 1-4)
            smooth_ps : float, default=2.5
                box filter [:math:`\\rm \mu Hz`] to smooth PS smoothing before computing the ACF 
            threshold : float, default=1.0
                fractional width of FWHM to use in ACF for later iterations 
            upper_osc : float, default=None
                upper frequency bound of the power spectrum used to calculate the :term:`ACF` 
            hey : bool, default=False
                plugin for Daniel Hey's echelle package **(NOT CURRENTLY IMPLEMENTED YET)**
            samples : bool, default=False
                save samples from the sampling steps **Note:** now seed is saved so they are reproducible regardless

        Attributes
            params : Dict[str,Dict[,]]
                the updated parameters

        """
        globe = dict(
            cmap = cmap,
            clip_value = clip_value,
            fft = fft,
            globe = globe,
            interp_ech = interp_ech,
            lower_osc = lower_osc,
            models = models,
            mc_iter = mc_iter,
            nox = nox,
            noy = noy,
            npb = npb,
            n_peaks = n_peaks,
            numax = numax,
            osc_width = osc_width,
            smooth_ech = smooth_ech,
            sm_par = sm_par,
            smooth_ps = smooth_ps,
            threshold = threshold,
            upper_osc = upper_osc,
            hey = hey,
            samples = samples,
        )
        self.params.update(globe)


    def add_stars(self, stars=None):
        if stars is not None:
            self.params['stars'] = stars
        else:
            raise PySYDInputError("ERROR: no star provided")
        self.assign_stars()


    def assign_stars(self,):
        """Add stars

        This routine will load in target stars, sets up "groups" (relevant for parallel
        processing) and then load in the relevant information


        """
        # Set file paths and make directories if they don't yet exist
        for star in self.params['stars']:
            self.params[star] = {}
            self.params[star]['path'] = os.path.join(self.params['outdir'], str(star))
            if self.params['save'] and not os.path.exists(self.params[star]['path']):
                os.makedirs(self.params[star]['path'])
        self._get_groups()
        self._add_info()


    def star_list(self,):
        """Load star list

        If no stars have been provided yet, it will read in the default text file
        (and if that does not exist, it will raise an error)

        """
        if not os.path.exists(self.params['todo']):
            raise PySYDInputError("ERROR: no stars or star list provided")
        else:
            with open(self.params['todo'], "r") as f:
                self.params['stars'] = [line.strip().split()[0] for line in f.readlines()]


    def _get_groups(self, n_threads=0,):
        """Get star groups
    
        Mostly relevant for parallel processing -- which sets up star groups to run 
        in parallel based on the number of threads

        """
        if hasattr(self, 'mode') and self.params['mode'] == 'parallel':
            todo = np.array(self.params['stars'])
            if self.params['n_threads'] == 0:
                self.params['n_threads'] = mp.cpu_count()
            if len(todo) < self.params['n_threads']:
                self.params['n_threads'] = len(todo)
            # divide stars into groups set by number of cpus/nthreads available
            digitized = np.digitize(np.arange(len(todo)) % self.params['n_threads'], np.arange(self.params['n_threads']))
            self.params['groups'] = np.array([todo[digitized == i] for i in range(1, self.params['n_threads']+1)], dtype=object)
        else:
            self.params['groups'] = np.array(self.params['stars'])


    def _add_info(self):
        """Add info

        Checks and saves all default information for stars separately


        """
        self.get_info()
        for star in self.params['stars']:
            if self.params[star]['numax'] is not None:
                self.params[star]['estimate'] = False
                if self.params[star]['dnu'] is not None:
                    self.params[star]['force'] = self.params[star]['dnu']
                self.params[star]['dnu'] = delta_nu(self.params[star]['numax'])
            else:
                if 'rs' in self.params[star] and self.params[star]['rs'] is not None and \
                  'logg' in self.params[star] and self.params[star]['logg'] is not None:
                    self.params[star]['ms'] = ((((self.params[star]['rs']*self.constants['r_sun'])**(2.0))*10**(self.params[star]['logg'])/self.constants['G'])/self.constants['m_sun'])
                    self.params[star]['numax'] = self.constants['numax_sun']*self.params[star]['ms']*(self.params[star]['rs']**(-2.0))*((self.params[star]['teff']/self.constants['teff_sun'])**(-0.5))
                    self.params[star]['dnu'] = self.constants['dnu_sun']*(self.params[star]['ms']**(0.5))*(self.params[star]['rs']**(-1.5))  
            if self.params[star]['lower_ech'] is not None and self.params[star]['upper_ech'] is not None:
                self.params[star]['ech_mask'] = [self.params[star]['lower_ech'], self.params[star]['upper_ech']]
            else:
                self.params[star]['ech_mask'] = None


    def get_info(self):
        """Load star info
    
        This function retrieves any and all information available for any targets and the
        order is important here. The main dictionary is either the command-line arguments
        or all the defaults that were loaded in *but* this can be different on a single
        star basis and therefore we need to handle this in special steps:
         #. first initializes all keys for each star
         #. copy values from the csv file when applicable
         #. copy defaults when value is not available
         #. any command-line arguments override previous assignments

        .. todo:: if unsure, can (re)set up this file with a simple command


        """
        columns = get_dict(type='columns')
        # Create all keys first
        for star in self.params['stars']:
            for column in columns['all']:
                if column in self.params:
                    self.params[star][column] = self.params[column]
                else:
                    self.params[star][column] = None

        # Open csv file if it exists
        if os.path.exists(self.params['info']) and not self.params['ignore']:
            df = pd.read_csv(self.params['info'])
            stars = [str(each) for each in df.stars.values.tolist()]
            for star in self.params['stars']:
                if str(star) in stars:
                    idx = stars.index(str(star))
                    # Update information from columns
                    for column in df.columns.values.tolist():
                        if not np.isnan(df.loc[idx,column]):
                            if column in columns['int']:
                                self.params[star][column] = int(df.loc[idx,column])
                            elif column in columns['float']:
                                self.params[star][column] = float(df.loc[idx,column])
                            elif column in columns['bool']:
                                self.params[star][column] = df.loc[idx,column]
                            elif column in columns['str']:
                                self.params[star][column] = str(df.loc[idx,column])
                            else:
                                pass

        if not self.params['cli']:
            return
        # CLI will override anything from before
        for column in get_dict(type='columns')['override']:
            if self.override[column] is not None:
                for i, star in enumerate(self.params['stars']):
                    self.params[star][column] = self.override[column][i]


    def _add_cli(self, args):
        """Add CLI

        Save any non-default parameters provided via command line but skips over any keys
        in the override columns since those are star specific and have a given length --
        it will come back to this

        Parameters
            args : argparse.Namespace
                the command line arguments


        """
        if args.cli:
            self.check_cli(args)
            # CLI options overwrite defaults
            for key, value in args.__dict__.items():
                # Make sure it is not a variable with a >1 length
                if key not in self.override:
                    self.params[key] = value

            # were stars provided
            if self.params['stars'] is None:
                self.star_list()
        else:
            self.params['stars'] = args.stars


    def check_cli(self, args, max_laws=3):
        """Check CLI
    
        Make sure that any command-line inputs are the proper lengths, types, etc.

        Parameters
            args : argparse.Namespace
                the command line arguments
            max_laws : int, default=3
                maximum number of resolvable Harvey components

        Asserts
            - the length of each array provided (in override) is equal
            - the oversampling factor is an integer (if applicable)
            - the number of Harvey laws to "force" is an integer (if applicable)

        """
        self.override = {
            'numax': args.numax,
            'dnu': args.dnu,
            'lower_ex': args.lower_ex,
            'upper_ex': args.upper_ex,
            'lower_bg': args.lower_bg,
            'upper_bg': args.upper_bg,
            'lower_ps': args.lower_ps,
            'upper_ps': args.upper_ps,
            'lower_ech': args.lower_ech,
            'upper_ech': args.upper_ech,
        }
        for each in self.override:
            if self.override[each] is not None:
                assert len(args.stars) == len(self.override[each]), "The number of values provided for %s does not equal the number of stars"%each
        if args.oversampling_factor is not None:
            assert isinstance(args.oversampling_factor, int), "The oversampling factor for the input PS must be an integer"
        if args.n_laws is not None:
            assert args.n_laws <= max_laws, "We likely cannot resolve %d Harvey-like components for point sources. Please select a smaller number."%args.n_laws


def get_dict(type='params'):
    """Get dictionary
    
    Quick+convenient utility function to read in longer dictionaries that are used throughout
    the software

    Parameters
        type : {'columns','params','plots','tests','functions'}, default='params'
            which dictionary to load in -- which *MUST* match their relevant filenames

    Returns
        result : Dict[str,Dict[,]]
            the relevant (type) dictionary

    .. important:: 
       `'functions'` cannot be saved and loaded in like the other dictionarie because it
       points to modules loaded in from another file 

    """
    if type == 'functions':
        return {
                0: lambda white_noise : (lambda frequency : models._harvey_none(frequency, white_noise)),
                1: lambda frequency, white_noise : models._harvey_none(frequency, white_noise), 
                2: lambda white_noise : (lambda frequency, tau_1, sigma_1 : models._harvey_one(frequency, tau_1, sigma_1, white_noise)), 
                3: lambda frequency, tau_1, sigma_1, white_noise : models._harvey_one(frequency, tau_1, sigma_1, white_noise), 
                4: lambda white_noise : (lambda frequency, tau_1, sigma_1, tau_2, sigma_2 : models._harvey_two(frequency, tau_1, sigma_1, tau_2, sigma_2, white_noise)), 
                5: lambda frequency, tau_1, sigma_1, tau_2, sigma_2, white_noise : models._harvey_two(frequency, tau_1, sigma_1, tau_2, sigma_2, white_noise),
                6: lambda white_noise : (lambda frequency, tau_1, sigma_1, tau_2, sigma_2, tau_3, sigma_3 : models._harvey_three(frequency, tau_1, sigma_1, tau_2, sigma_2, tau_3, sigma_3, white_noise)),
                7: lambda frequency, tau_1, sigma_1, tau_2, sigma_2, tau_3, sigma_3, white_noise : models._harvey_three(frequency, tau_1, sigma_1, tau_2, sigma_2, tau_3, sigma_3, white_noise),
               }
    path = os.path.join(os.path.dirname(__file__), 'dicts', '%s.dict'%type)
    with open(path, 'r') as f:
        return ast.literal_eval(f.read())


def _save_file(x, y, path, overwrite=False, formats=[">15.8f", ">18.10e"]):
    """Saves basic text files
    
    After determining the best-fit stellar background model, this module
    saved the background-subtracted power spectrum

    Parameters
        x : numpy.ndarray
            the independent variable i.e. the time or frequency array 
        y : numpy.ndarray
            the dependent variable, in this case either the flux or power array
        path : str
            absolute path to save file to
        overwrite : bool, optional
            whether to overwrite existing files or not
        formats : List[str]
            2x1 list of formats to save arrays as


    """
    if os.path.exists(path) and not overwrite:
        path = _get_next(path)
    with open(path, "w") as f:
        for xx, yy in zip(x, y):
            values = [xx, yy]
            text = '{:{}}'*len(values) + '\n'
            fmt = sum(zip(values, formats), ())
            f.write(text.format(*fmt))


def _get_next(path, count=1):
    """
    Get next integer
    
    When the overwriting of files is disabled, this module determines what
    the last saved file was 

    Parameters
        path : str
            absolute path to file name that already exists
        count : int
            starting count, which is incremented by 1 until a new path is determined

    Returns
        new_path : str
            unused path name


    """
    path, fname = os.path.split(path)[0], os.path.split(path)[-1]
    new_fname = '%s_%d.%s'%(fname.split('.')[0], count, fname.split('.')[-1])
    new_path = os.path.join(path, new_fname)
    if os.path.exists(new_path):
        while os.path.exists(new_path):
            count += 1
            new_fname = '%s_%d.%s'%(fname.split('.')[0], count, fname.split('.')[-1])
            new_path = os.path.join(path, new_fname)
    return new_path


def _save_estimates(star, variables=['star', 'numax', 'dnu', 'snr']):
    """
    
    Saves the parameter estimates (i.e. results from first module)

    Parameters
        star : pysyd.target.Target
            processed pipeline target
        variables : List[str]
            list of estimated variables to save (e.g., :math:`\\rm \\nu_{max}`, :math:`\\Delta\\nu`)

    Returns
        star : pysyd.target.Target
            updated pipeline target

    """
    if 'best' in star.params:
        best = star.params['best']
        results = [star.name, star.params['results']['estimates'][best]['numax'], star.params['results']['estimates'][best]['dnu'], star.params['results']['estimates'][best]['snr']]
        save_path = os.path.join(star.params['path'], 'estimates.csv')
        if not star.params['overwrite']:
            save_path = _get_next(save_path)
        ascii.write(np.array(results), save_path, names=variables, delimiter=',', overwrite=True)


def _save_parameters(star, results={}, cols=['parameter', 'value', 'uncertainty']):
    """
    
    Saves the derived global parameters 

    Parameters
        star : pysyd.target.Target
            pipeline target with the results of the global fit
        results : Dict[str,float]
            parameter estimates from the pipeline
        cols : List[str]
            columns used to construct a pandas dataframe

    """
    results = star.params['results']['parameters']
    df = pd.DataFrame(results)
    star.df = df.copy()
    new_df = pd.DataFrame(columns=cols)
    for c, col in enumerate(df.columns.values.tolist()):
        new_df.loc[c, 'parameter'] = col
        new_df.loc[c, 'value'] = df.loc[0,col]
        if star.params['mc_iter'] > 1:
            new_df.loc[c, 'uncertainty'] = mad_std(df[col].values)
        else:
            new_df.loc[c, 'uncertainty'] = '--'
    save_path = os.path.join(star.params['path'], 'global.csv')
    if not star.params['overwrite']:
        save_path = _get_next(save_path)
    new_df.to_csv(save_path, index=False)
    if star.params['samples']:
        save_path = os.path.join(star.params['path'], 'samples.csv')
        if not star.params['overwrite']:
            save_path = _get_next(save_path)
        df.to_csv(save_path, index=False)
    if star.params['mc_iter'] > 1:
        star.params['plotting']['samples'] = {'df':star.df.copy()}


def _verbose_output(star, note=''):
    """

    Prints verbose output from the global fit 


    """
    params = get_dict()
    if not star.params['overwrite']:
        list_of_files = glob.glob(os.path.join(star.params['path'], 'global*'))
        file = max(list_of_files, key=os.path.getctime)
    else:
        file = os.path.join(star.params['path'], 'global.csv')
    df = pd.read_csv(file)
    note += '-----------------------------------------------------------\nOutput parameters\n-----------------------------------------------------------'
    if star.params['mc_iter'] > 1:
        line = '\n%s: %.2f +/- %.2f %s'
        for idx in df.index.values.tolist():
            note += line%(df.loc[idx,'parameter'], df.loc[idx,'value'], df.loc[idx,'uncertainty'], params[df.loc[idx,'parameter']]['unit'])
    else:
        line = '\n%s: %.2f %s'
        for idx in df.index.values.tolist():
            note += line%(df.loc[idx,'parameter'], df.loc[idx,'value'], params[df.loc[idx,'parameter']]['unit'])
    note+='\n-----------------------------------------------------------'
    print(note)


def scrape_output(args):
    """Concatenate results
    
    Automatically concatenates and summarizes the results for all processed stars in each
    of the two submodules

    Methods
        :mod:`pysyd.utils._sort_table`
    

    """
    # Estimate outputs
    if glob.glob(os.path.join(args.params['outdir'],'**','estimates*csv')):
        df = pd.DataFrame(columns=['star','numax','dnu','snr'])
        files_estimates = glob.glob(os.path.join(args.params['outdir'],'**','estimates*csv'))
        # get which stars have this output
        dirs = list(set([os.path.split(os.path.split(file)[0])[-1] for file in files_estimates]))
        # iterate through stars
        for dir in dirs:
            list_of_files = glob.glob(os.path.join(args.params['outdir'],dir,'estimates*csv'))
            file = max(list_of_files, key=os.path.getctime)
            df_new = pd.read_csv(file)
            df = pd.concat([df, df_new])
        df = _sort_table(df)
        df.to_csv(os.path.join(args.params['outdir'],'estimates.csv'), index=False)

    # Parameter outputs
    if glob.glob(os.path.join(args.params['outdir'],'**','global*csv')):
        df = pd.DataFrame(columns=['star'])
        files_globals = glob.glob(os.path.join(args.params['outdir'],'**','global*csv'))
        dirs = list(set([os.path.split(os.path.split(file)[0])[-1] for file in files_globals]))
        for dir in dirs:
            list_of_files = glob.glob(os.path.join(args.params['outdir'],dir,'global*csv'))
            file = max(list_of_files, key=os.path.getctime)
            df_temp = pd.read_csv(file)
            columns = ['star'] + df_temp['parameter'].values.tolist()
            values = [dir] + df_temp['value'].values.tolist()
            if df_temp['uncertainty'].values.tolist()[0] != '--':
                columns += ['%s_err'%col for col in df_temp['parameter'].values.tolist()]
                values += df_temp['uncertainty'].values.tolist()
            # adjust format to be like the final csv
            df_new = pd.DataFrame(columns=columns)
            df_new.loc[0] = np.array(values)
            length = len(df)
            # makes sure all columns are in final csv
            for column in df_new.columns.values.tolist():
                if column not in df.columns.values.tolist():
                    df[column] = np.nan
                # copy value
                df.loc[length,column] = df_new.loc[0,column]
        df = _sort_table(df)
        df.to_csv(os.path.join(args.params['outdir'],'global.csv'), index=False)


def _sort_table(df, one=[], two=[],):
    df.set_index('star', inplace=True, drop=True)
    for star in df.index.values.tolist():
        alpha, numeric = 0, 0
        for char in str(star):
            if not char.isalpha():
                numeric += 1
            else:
                alpha += 1
        if alpha == 0:
            one.append(star)
        else:
            two.append(star)
    # sort integers
    one = [str(sort) for sort in sorted([int(each) for each in one])]
    final = one + sorted(two)
    df = df.reindex(final, copy=True)
    df.reset_index(drop=False, inplace=True)
    return df


def max_elements(x, y, npeaks, distance=None, exp_dnu=None):
    """N highest peaks
    
    Module to obtain the x and y values for the n highest peaks in a 2D array 

    Parameters
        x, y : numpy.ndarray, numpy.ndarray
            the series of data to identify peaks in
        npeaks : int, default=5
            the first n peaks
        distance : float, default=None
            used in :mod:`scipy.find_peaks` if not `None`
        exp_dnu : float, default=None
            if not `None`, multiplies y array by Gaussian weighting centered on `exp_dnu`

    Returns
        peaks_x, peaks_y : numpy.ndarray, numpy.ndarray
            the x & y coordinates of the first n peaks `npeaks`


    """
    xx, yy = np.copy(x), np.copy(y)
    weights = np.ones_like(yy)
    # if exp_dnu is not None, use weighting technique
    if exp_dnu is not None:
        sig = 0.35*exp_dnu/2.35482 
        weights *= np.exp(-(xx-exp_dnu)**2./(2.*sig**2))*((sig*np.sqrt(2.*np.pi))**-1.)
    yy *= weights
    # provide threshold for finding peaks
    if distance is not None:
        peaks_idx, _ = find_peaks(yy, distance=distance)
    else:
        peaks_idx, _ = find_peaks(yy)
    # take from original (unweighted) arrays 
    px, py = x[peaks_idx], y[peaks_idx]
    # sort by n highest peaks
    s = np.argsort(py)
    peaks_y = py[s][-int(npeaks):][::-1]
    peaks_x = px[s][-int(npeaks):][::-1]
    return list(peaks_x), list(peaks_y), weights


def return_max(x, y, exp_dnu=None,):
    """Return max
    
    Return the peak (and/or the index of the peak) in a given 2D array

    Parameters
        x, y : numpy.ndarray, numpy.ndarray
            the independent and dependent axis, respectively
        exp_dnu : Required[float]
            the expected dnu. Default value is `None`.

    Returns
        idx : int
            **New**: *always* returns the index first, followed by the corresponding peak from the x+y arrays
        xx[idx], yy[idx] : Union[int, float], Union[int, float]
            corresponding peak in the x and y arrays

    """
    xx, yy = np.copy(x), np.copy(y)
    if list(yy) != []:
        if exp_dnu is not None:
            lst = list(np.absolute(xx-exp_dnu))
            idx = lst.index(min(lst))
        else:
            lst = list(yy)
            idx = lst.index(max(lst))
    else:
        return None, np.nan, np.nan
    return idx, xx[idx], yy[idx]


def _bin_data(x, y, width, log=False, mode='mean'):
    """Bin data
    
    Bins 2D series of data

    Parameters
        x, y : numpy.ndarray, numpy.ndarray
            the x and y values of the data
        width : float
            bin width (typically in :math:`\\rm \\mu Hz`)
        log : bool, default=False
            creates equal bin sizes in logarithmic space when `True`

    Returns
        bin_x, bin_y, bin_yerr : numpy.ndarray, numpy.ndarray, numpy.ndarray
            binned arrays (and error is computed using the standard deviation)

    """
    if log:
        mi = np.log10(min(x))
        ma = np.log10(max(x))
        no = np.int(np.ceil((ma-mi)/width))
        bins = np.logspace(mi, mi+(no+1)*width, no)
    else:
        bins = np.arange(min(x), max(x)+width, width)

    digitized = np.digitize(x, bins)
    if mode == 'mean':
        bin_x = np.array([x[digitized == i].mean() for i in range(1, len(bins)) if len(x[digitized == i]) > 0])
        bin_y = np.array([y[digitized == i].mean() for i in range(1, len(bins)) if len(x[digitized == i]) > 0])
    elif mode == 'median':
        bin_x = np.array([np.median(x[digitized == i]) for i in range(1, len(bins)) if len(x[digitized == i]) > 0])
        bin_y = np.array([np.median(y[digitized == i]) for i in range(1, len(bins)) if len(x[digitized == i]) > 0])
    else:
        pass
    bin_yerr = np.array([y[digitized == i].std()/np.sqrt(len(y[digitized == i])) for i in range(1, len(bins)) if len(x[digitized == i]) > 0])
    return bin_x, bin_y, bin_yerr


def _ask_int(question, n_trials, max_attempts=100, count=1, special=False):    
    """Integer input
    
    Asks for an integer input -- this is specifically formatted for the module that searches
    and identifies power excess due to solar-like oscillations and then estimates its properties.
    Therefore it forces a selection that matches with one of the (n_)trials or accepts zero to 
    provide your own estimate for :math:`\\rm \\nu_{max}` directly

    Parameters
        question : str
            the statement and/or question that needs to be answered
        max_attempts : int, default=100
            the maximum number of tries a user has before breaking
        count : int
            the attempt number
        special : bool, default=False
            changes to `True` if the input is zero, changing the integer requirement to
            a float to provide :term:`numax`

    Returns
        answer : int
            the provided user input (either an integer corresponding to the trial number or
            a numax estimate) *or* `None` if number of attemps exceeded `max_attempts`


    """
    print()
    while count < max_attempts:
        answer = input(question)
        try:
            if special:
                try:
                    value = float(answer)
                except ValueError:
                    print('ERROR: please try again ')
                else:
                    return value
            elif float(answer).is_integer() and not special:
                if int(answer) == 0:
                    special = True
                    question = '\nWhat is your value for numax? '
                elif int(answer) >= 1 and int(answer) <= n_trials:
                    return int(answer)
                else:
                    print('ERROR: please select an integer between 1 and %d \n       (or 0 to provide your own value for numax)\n'%n_trials)
            else:
                print("ERROR: the selection must match one of the integer values \n")
        except ValueError:
            print("ERROR: not a valid response \n")
        count += 1
    return None


def _get_results(suffixes=['_idl', '_py'], max_numax=3200.,):
    """

    Load and compare results between `SYD` and `pySYD` pipelines

    Parameters
        file_idlsyd : str
            path to ``SYD`` ensemble results
        file_pysyd : str
            path to ``pySYD`` ensemble results
        suffixes : List[str]
            extensions to use when merging the two pipeline results
        max_numax : float, optional
            maximum values to use for numax comparison

    Returns
        df : pandas.DataFrame
            pandas dataframe with merged results

    """
    # load in both pipeline results
    idlsyd = pd.read_csv(SYDFILE, skiprows=20, delimiter='|', names=get_dict('columns')['syd'])
    pysyd = pd.read_csv(PYSYDFILE)
    # make sure they can crossmatch
    idlsyd.KIC = idlsyd.KIC.astype(str)
    pysyd.star = pysyd.star.astype(str)
    # merge measurements from syd & pySYD catalogs
    df = pd.merge(idlsyd, pysyd, left_on='KIC', right_on='star', how='inner', suffixes=suffixes)
    df = df[df['numax_smooth'] <= max_numax]
    return df


def delta_nu(numax):
    """:math:`\\Delta\\nu`
    
    Estimates the large frequency separation using the numax scaling relation (add citation?)

    Parameters
        numax : float
            the frequency corresponding to maximum power or numax (:math:`\\rm \\nu_{max}`)

    Returns
        dnu : float
            the approximated frequency spacing or dnu (:math:`\\Delta\\nu`)

    """

    return 0.22*(numax**0.797)


def _fix_init(path=None, row=8):
    import pysyd
    with open(pysyd.__file__, "r") as f:
        lines = [line for line in f.readlines()]
    if path is None:
        line = "_ROOT = os.path.abspath(os.path.dirname(__file__))\n"
    else:
        line = "_ROOT = %s\n"%path
    lines[row] = line
    with open(pysyd.__file__, "w") as f:
        for line in lines:
            f.write(line)


def _download_all(raw='https://raw.githubusercontent.com/ashleychontos/pySYD/master/dev/', 
                  note='', dl={},):

    # INFO DIRECTORY
    note, dl = _download_info(raw, note, dl)
    # DATA DIRECTORY
    note, dl = _download_data(raw, note, dl)
    # RESULTS DIRECTORY
    note = _download_results(note)
    # Download files that do not already exist
    if dl:
        # downloading example data will generate output in terminal, so always include this regardless
        print('\nDownloading relevant data from source directory:')
        for infile, outfile in dl.items():
            subprocess.call(['curl %s > %s'%(infile, outfile)], shell=True)
    return note



def _download_info(raw, note, dl):
    """Make info directory

    """
    from pysyd import INFDIR
    # create info directory (INFDIR)
    if not os.path.exists(INFDIR):
        os.mkdir(INFDIR)
        note+=' - created input file directory at %s \n'%INFDIR
    # example input files   
    outfile1 = os.path.join(INFDIR, args.todo)               # example star list file
    if not os.path.exists(outfile1):
        dl.update({'%sinfo/todo.txt'%raw:outfile1})
        note+=' - saved an example of a star list\n'                               
    outfile2 = os.path.join(INFDIR, args.info)               # example star info file
    if not os.path.exists(outfile2):
        dl.update({'%sinfo/star_info.csv'%raw:outfile2})
        note+=' - saved an example for the star information file\n'
    return note, dl


def _download_data(raw, note, dl, save=False):
    """Make data directory

    """
    from pysyd import INPDIR
    # create data directory (INPDIR)
    if not os.path.exists(INPDIR):
        os.mkdir(INPDIR)
        note+=' - created data directory at %s \n'%INPDIR
    # example data
    for target in ['1435467', '2309595', '11618103']:
        for ext in ['LC', 'PS']:
            infile='%sdata/%s_%s.txt'%(raw, target, ext)
            outfile=os.path.join(INPDIR, '%s_%s.txt'%(target, ext))
            if not os.path.exists(outfile):
                save=True
                dl.update({infile:outfile})
    if save:
        note+=' - example data saved to data directory\n'
    return note, dl


def _download_results():
    """Make results directory

    """
    from pysyd import OUTDIR
    # create results directory (OUTDIR)
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)
        note+=' - results will be saved to %s\n'%OUTDIR
    return note


def _save_status(file, section, params):
    """

    Save pipeline status

    Parameters
        file : str 
            name of output config file
        section : str
            name of section in config file
        params : Dict() 
            dictionary of all options to populate in the specified section


    """
    import configparser
    config = configparser.ConfigParser()

    if os.path.isfile(file):
        config.read(file)

    if not config.has_section(section):
        config.add_section(section)

    for key, val in params.items():
        config.set(section, key, val)

    with open(file, 'w') as f:
        config.write(f)


def _load_status(file):
    """

    Load pipeline status

    Parameters
        file : str
            name of output config file

    Returns
        config : configparser.ConfigParser
            config file with pipeline status

    """

    config = configparser.ConfigParser()
    gl = config.read(file)

    return config