import os
import argparse










# Package mode
import pysyd
from pysyd import pipeline
from pysyd import INFDIR, INPDIR, OUTDIR


def main():

    parser = argparse.ArgumentParser(
                                     description="pySYD: automated measurements of global asteroseismic parameters", 
                                     prog='pySYD',
    )
    parser.add_argument('--version',
                        action='version',
                        version="%(prog)s {}".format(pysyd.__version__),
                        help="Print version number and exit.",
    )

#### HIGH-LEVEL FUNCTIONALITY

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--cli',
                               dest='cli',
                               help='Running from command line (this should not be touched)',
                               default=True,
                               action='store_false',
    )
    parent_parser.add_argument('--in', '--input', '--inpdir', 
                               metavar='str',
                               dest='inpdir',
                               help='input or data directory',
                               type=str,
                               default=INPDIR,
    )
    parent_parser.add_argument('--infdir',
                               metavar='str',
                               dest='infdir',
                               help='info directory',
                               type=str,
                               default=INFDIR,
    )
    parent_parser.add_argument('--out', '--outdir', '--output',
                               metavar='str',
                               dest='outdir',
                               help='output (i.e. results) directory',
                               type=str,
                               default=OUTDIR,
    )
    parent_parser.add_argument('-o', '--overwrite',
                               dest='overwrite',
                               help='Overwrite existing files with the same name/path',
                               default=False, 
                               action='store_true',
    )
    parent_parser.add_argument('-p', '--show', '--plot', 
                               dest='show',
                               help='show output figures',
                               default=False, 
                               action='store_true',
    )
    parent_parser.add_argument('-r', '--ret', '--return',
                               dest='ret',
                               help='enable the returning of output in an interactive session (default = `False`)',
                               default=False, 
                               action='store_true',
    )
    parent_parser.add_argument('-s', '--save',
                               dest='save',
                               help='Do not save output figures and results.',
                               default=True, 
                               action='store_false',
    )
    parent_parser.add_argument('-t', '--test',
                               dest='test',
                               help='test software functionality',
                               default=False, 
                               action='store_true',
    )
    parent_parser.add_argument('-v', '--verbose', 
                               dest='verbose',
                               help='turn on verbose output',
                               default=False, 
                               action='store_true',
    )

#### DATA-RELATED

    data_parser = argparse.ArgumentParser(add_help=False)
    data_parser.add_argument('--dnu',
                             metavar='float',
                             dest='dnu',
                             help='spacing to fold PS for mitigating mixed modes',
                             nargs='*',
                             type=float,
                             default=None, 
    )
    data_parser.add_argument('--gap', 
                             metavar='int',
                             dest='gap',
                             help="What constitutes a time series 'gap' (i.e. n x the cadence)",
                             type=int,
                             default=20, 
    )
    data_parser.add_argument('--info', 
                             metavar='str',
                             dest='info',
                             help='list of stellar parameters and options',
                             type=str,
                             default=os.path.join(INFDIR,'star_info.csv'),
    )
    data_parser.add_argument('-i', '--ignore',
                             dest='ignore',
                             help='quick way to ignore star info file (vs. changing all the settings via CLI)',
                             default=False,
                             action='store_true',
    )
    data_parser.add_argument('-k', '--kc', '--kepcorr', 
                             dest='kep_corr',
                             help='Turn on the Kepler short-cadence artefact correction routine',
                             default=False, 
                             action='store_true',
    )
    data_parser.add_argument('--lf', '--lowerf', '--lowerff', 
                             metavar='float', 
                             dest='lower_ff',
                             help='lower folded frequency limit to whiten mixed modes',
                             nargs='*',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('--ll', '--lowerl', '--lowerlc',
                             metavar='float', 
                             dest='lower_lc',
                             help='lower limit for time series data',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('--lp', '--lowerp', '--lowerps',
                             metavar='float', 
                             dest='lower_ps',
                             help='lower frequency limit of power spectrum',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('-n', '--notch', 
                             dest='notching',
                             help='another technique to mitigate effects from mixed modes (not fully functional, creates weirds effects for higher SNR cases??)',
                             default=False, 
                             action='store_true',
    )
    data_parser.add_argument('--of', '--over', 
                             metavar='int',
                             dest='oversampling_factor',
                             help='The oversampling factor (OF) of the input power spectrum',
                             type=int,
                             default=None,
    )
    data_parser.add_argument('--seed',
                             dest='seed',
                             help='save seed for reproducible results',
                             default=None,
                             type=int,
    )
    data_parser.add_argument('--star', '--stars',
                             metavar='str',
                             dest='stars',
                             help='List of stars to process',
                             type=str,
                             nargs='*',
                             default=None,
    )
    data_parser.add_argument('--todo', '--list',
                             metavar='str',
                             dest='todo',
                             help='list of stars to process',
                             type=str,
                             default=os.path.join(INFDIR,'todo.txt'),
    )
    data_parser.add_argument('--uf', '--upperf', '--upperff', 
                             metavar='float', 
                             dest='upper_ff',
                             help='upper folded frequency limit to whiten mixed modes',
                             nargs='*',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('--ul', '--upperl', '--upperlc',
                             metavar='float', 
                             dest='upper_lc',
                             help='upper limit for time series data',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('--up', '--upperp', '--upperps',
                             metavar='float', 
                             dest='upper_ps',
                             help='upper frequency limit of power spectrum',
                             default=None,
                             type=float,
    )
    data_parser.add_argument('-x', '--stitch', 
                             dest='stitch',
                             help="Correct for large gaps in time series data by 'stitching' the light curve",
                             default=False,
                             action='store_true',
    )

#### MAIN PARSER

    main_parser = argparse.ArgumentParser(add_help=False)

#### IDENTIFY & ESTIMATE

    estimate = main_parser.add_argument_group('Search parameters')
    estimate.add_argument('-a', '--ask',
                          dest='ask',
                          help='Ask which trial to use',
                          default=False, 
                          action='store_true',
    )
    estimate.add_argument('--bin', '--binning',
                          metavar='float',  
                          dest='binning', 
                          help='Binning interval for PS (in muHz)',
                          default=0.005, 
                          type=float,
    )
    estimate.add_argument('--bm', '--mode', 
                          metavar='str',
                          choices=["mean", "median", "gaussian"],
                          dest='bin_mode',
                          help='Binning mode',
                          default='mean',
                          type=str,
    )
    estimate.add_argument('-e', '--estimate',
                          dest='estimate',
                          help='Turn off the optional module that estimates numax',
                          default=True,
                          action='store_false',
    )
    estimate.add_argument('-j', '--adjust',
                          dest='adjust',
                          help='adjusts default parameters based on numax estimate',
                          default=False, 
                          action='store_true',
    )
    estimate.add_argument('--le', '--lowere', '--lowerse',
                          metavar='float', 
                          dest='lower_se',
                          help='Lower frequency limit of PS for searching+estimating',
                          nargs='*',
                          default=None,
                          type=float,
    )
    estimate.add_argument('--ntrials', '--trials', 
                          metavar='int', 
                          dest='n_trials',
                          default=3, 
                          type=int,
    )
    estimate.add_argument('--sw', '--smoothwidth',
                          metavar='float', 
                          dest='smooth_width',
                          help='Box filter width (in muHz) for smoothing the PS',
                          default=20.0,
                          type=float,
    )
    estimate.add_argument('--step', '--steps', 
                          metavar='float', 
                          dest='step', 
                          default=0.25,
                          type=float, 
    )
    estimate.add_argument('--ue', '--uppere', '--upperse',
                          metavar='float', 
                          dest='upper_se',
                          help='Upper frequency limit of PS for search+estimate',
                          nargs='*',
                          default=None,
                          type=float,
    )

#### BACKGROUND FIT

    background = main_parser.add_argument_group('Background parameters')
    background.add_argument('-b', '--bg', '--background',
                            dest='background',
                            help='Turn off the routine that determines the stellar background contribution',
                            default=True,
                            action='store_false',
    )
    background.add_argument('--basis', 
                            metavar='str',
                            dest='basis',
                            help="Which basis to use for background fit (i.e. 'a_b', 'pgran_tau', 'tau_sigma'), *** NOT operational yet ***",
                            default='tau_sigma', 
                            type=str,
    )
    background.add_argument('--bf', '--box', '--boxfilter',
                            metavar='float', 
                            dest='box_filter',
                            help='Box filter width [in muHz] for plotting the PS',
                            default=1.0,
                            type=float,
    )
    background.add_argument('--iw', '--indwidth',
                            metavar='float', 
                            dest='ind_width', 
                            help='Width of binning for PS [in muHz]',
                            default=20.0, 
                            type=float,
    )
    background.add_argument('--laws', '--nlaws', 
                            metavar='int', 
                            dest='n_laws', 
                            help='Force number of red-noise component(s)',
                            default=None, 
                            type=int,
    )
    background.add_argument('--lb', '--lowerb', '--lowerbg',
                            metavar='float', 
                            dest='lower_bg',
                            help='Lower frequency limit of PS',
                            nargs='*',
                            default=None,
                            type=float,
    )
    background.add_argument('--metric', 
                            metavar='str', 
                            dest='metric', 
                            help="Which model metric to use, choices=['bic','aic']",
                            default='bic', 
                            type=str,
    )
    background.add_argument('-m', '--models', 
                            dest='models',
                            help='include plot with different bgmodel fits',
                            default=False,
                            action='store_true',
    )
    background.add_argument('--nrms', '--rms',  
                            metavar='int', 
                            dest='n_rms', 
                            help='Number of points to estimate the amplitude of red-noise component(s)',
                            default=20, 
                            type=int,
    )
    background.add_argument('--ub', '--upperb', '--upperbg',
                            metavar='float', 
                            dest='upper_bg',
                            help='Upper frequency limit of PS',
                            nargs='*',
                            default=None,
                            type=float,
    )
    background.add_argument('-w', '--wn', '--fixwn',
                            dest='fix_wn',
                            help='Fix the white noise level',
                            default=False,
                            action='store_true',
    )

#### GLOBAL PARAMETERS

    globe = main_parser.add_argument_group('Global parameters')
    globe.add_argument('--cm', '--color', 
                       metavar='str',
                       dest='cmap',
                       help='colormap of echelle diagram (default = `binary`) 
                       default='binary', 
                       type=str,
    )
    globe.add_argument('--cv', '--value',
                       metavar='float', 
                       dest='clip_value',
                       help='Clip value multiplier to use for echelle diagram (ED). Default is 3x the median, where clip_value == `3`.',
                       default=3.0, 
                       type=float,
    )
    globe.add_argument('--fft',
                       dest='fft',
                       help='Use :mod:`numpy.correlate` instead of fast fourier transforms to compute the ACF',
                       default=True,
                       action='store_false',
    )
    globe.add_argument('-g', '--globe', '--global',
                       dest='globe',
                       help='Disable the main global-fitting routine',
                       default=True,
                       action='store_false',
    )
    globe.add_argument('--ie', '--interpech',
                       dest='interp_ech',
                       help='turn on the interpolation of the output ED',
                       default=False,
                       action='store_true',
    )
    globe.add_argument('--lo', '--lowero', '--lowerosc',
                       metavar='float', 
                       dest='lower_osc',
                       help='lower frequency limit for the envelope of oscillations',
                       nargs='*',
                       default=None,
                       type=float,
    )
    globe.add_argument('--mc', '--iter', '--mciter', 
                       metavar='int', 
                       dest='mc_iter', 
                       help='number of Monte-Carlo iterations to run for estimating uncertainties (typically 200 is sufficient)',
                       default=1, 
                       type=int,
    )
    globe.add_argument('--nox', '--nacross',
                       metavar='int', 
                       dest='nox',
                       help='number of bins to use on the x-axis of the ED (currently being tested)',
                       default=None,
                       type=int, 
    )
    globe.add_argument('--noy', '--norders',
                       metavar='str', 
                       dest='noy',
                       help='NEW!! Number of orders to plot pm how many orders to shift (if ED is not centered)',
                       default='0+0',
                       type=str,
    )
    globe.add_argument('--npb',
                       metavar='int',
                       dest='npb',
                       help='NEW!! npb == "number per bin", which is option instead of nox that uses the frequency resolution and spacing to compute an appropriate bin size for the ED',
                       default=20,
                       type=int,
    )
    globe.add_argument('--npeaks', '--peaks', 
                       metavar='int', 
                       dest='n_peaks', 
                       help='number of peaks to fit in the ACF',
                       default=5, 
                       type=int,
    )
    globe.add_argument('--numax',
                       metavar='float',
                       dest='numax',
                       help='initial estimate for numax to bypass the forst module',
                       nargs='*',
                       default=None,
                       type=float,
    )
    globe.add_argument('--ow', '--oscwidth',
                       metavar='float', 
                       dest='osc_width',
                       help='fractional value of width to use for power excess, where width is computed using a solar scaling relation.',
                       default=1.0,
                       type=float,
    )
    globe.add_argument('--se', '--smoothech',
                       metavar='float', 
                       dest='smooth_ech',
                       help='Smooth ED using a box filter [in muHz]',
                       default=None,
                       type=float,
    )
    globe.add_argument('--sm', '--smpar',
                       metavar='float', 
                       dest='sm_par',
                       help='smoothing parameter used to estimate the smoothed numax (typically before 1-4 through experience -- **development purposes only**)',
                       default=None, 
                       type=float,
    )
    globe.add_argument('--sp', '--smoothps',
                       metavar='float', 
                       dest='smooth_ps',
                       help='box filter width [in muHz] of PS for ACF', 
                       type=float,
                       default=2.5,
    )
    globe.add_argument('--aw', '--acfwidth',
                       metavar='float', 
                       dest='acf_width',
                       help='fractional value of the FWHM to use in the ACF cutout',
                       default=1.0,
                       type=float,
    )
    globe.add_argument('--uo', '--uppero', '--upperosc',
                       metavar='float', 
                       dest='upper_osc',
                       help='upper frequency limit for the envelope of oscillations',
                       nargs='*',
                       default=None,
                       type=float,
    )
    globe.add_argument('-y', '--hey',
                       dest='hey', 
                       help="plugin for Daniel Hey's echelle package **not currently implemented**",
                       default=False, 
                       action='store_true',
    )
    globe.add_argument('-z', '--samples', 
                       dest='samples',
                       help='save samples from the Monte-Carlo sampling',
                       default=False, 
                       action='store_true',
    )


###################
# Different modes #
###################

    sub_parser = parser.add_subparsers(title='pySYD modes', dest='mode')

#### LOAD

    parser_load = sub_parser.add_parser('load',
                                        parents=[parent_parser, data_parser], 
                                        formatter_class=argparse.MetavarTypeHelpFormatter,
                                        help='Load in data for a given target',  
                                        )
    parser_load.add_argument('-c', '--cols', '--columns',
                             dest='columns',
                             help='Show columns of interest in a condensed format',
                             default=False,
                             action='store_true',
    )
    parser_load.add_argument('-d', '--data', 
                             dest='data',
                             help='Check data for a target',
                             default=True, 
                             action='store_false',
    )
    parser_load.add_argument('-r', '--ret', '--return',
                             dest='return',
                             help='enable returning of output in an interactive session',
                             default=True,
                             action='store_false',
    )
    parser_load.set_defaults(func=pipeline.load)

#### PARALLEL

    parser_parallel = sub_parser.add_parser('parallel', 
                                            help='Run pySYD in parallel',
                                            parents=[parent_parser, data_parser, main_parser],
                                            formatter_class=argparse.MetavarTypeHelpFormatter,
                                            )
    parser_parallel.add_argument('--nt', '--nthread', '--nthreads',
                                 metavar='int', 
                                 dest='n_threads',
                                 help='Number of processes to run in parallel',
                                 type=int,
                                 default=0,
    )
    parser_parallel.add_argument('-f', '--fix',
                                 dest='fix_wn',
                                 help='fix the white noise level',
                                 type=bool,
                                 default=False,
                                 action='store_true',
    )
    parser_parallel.set_defaults(func=pipeline.parallel)

#### PLOT

    parser_plot = sub_parser.add_parser('plot',
                                        help='Create and show relevant figures',
                                        parents=[parent_parser, data_parser], 
                                        formatter_class=argparse.MetavarTypeHelpFormatter,
                                        )
    parser_plot.add_argument('-c', '--compare', 
                             dest='compare',
                             help='Reproduce the *Kepler* legacy results',
                             default=False,
                             action='store_true',
    )
    parser_plot.add_argument('--results', 
                             dest='results',
                             help='Re-plot ``pySYD`` results for a single star',
                             default=False,
                             action='store_true',
    )
    parser_plot.set_defaults(func=pipeline.plot)

#### RUN

    parser_run = sub_parser.add_parser('run',
                                       help='Run the main pySYD pipeline',
                                       parents=[parent_parser, data_parser, main_parser], 
                                       formatter_class=argparse.MetavarTypeHelpFormatter,
                                       )
    parser_run.add_argument('-f', '--fix',
                            dest='fix_wn',
                            help='fix the white noise level',
                            type=bool,
                            default=False,
                            action='store_true',
    )
    parser_run.set_defaults(func=pipeline.run)

#### SETUP

    parser_setup = sub_parser.add_parser('setup', 
                                         parents=[parent_parser, data_parser], 
                                         formatter_class=argparse.MetavarTypeHelpFormatter,
                                         help='Easy setup of relevant directories and files',
                                         )
    parser_setup.add_argument('-a', '--all', 
                              dest='make_all',
                              help='Save all columns',
                              default=False, 
                              action='store_true',
    )
    parser_setup.add_argument('-f', '--fix',
                              dest='fix',
                              help='change root directory (where example data, etc. is saved)',
                              type=bool,
                              default=False,
                              action='store_true',
    )
    parser_setup.add_argument('--path', '--dir', '--directory',
                              metavar='str',
                              dest='path',
                              help='Path to save setup files to (default=os.getcwd()) **not functional yet',
                              type=str,
                              default=None,
    )
    parser_setup.set_defaults(func=pipeline.setup)

#### TEST

    parser_test = sub_parser.add_parser('test',
                                        parents=[parent_parser, data_parser, main_parser], 
                                        formatter_class=argparse.MetavarTypeHelpFormatter,
                                        help='Test different utilities (currently under development)',  
                                        )
    parser_test.add_argument('--methods', 
                             dest='methods',
                             help='compare different dnu methods',
                             default=False,
                             action='store_true',
    )
    parser_test.set_defaults(func=pipeline.test)

    args = parser.parse_args()
    if len(args.noy) == 1:
        args.noy = '%s+0'%args.noy
    elif len(args.noy) == 2:
        args.noy = '0%s'%args.noy
    else:
        pass
        
    args.func(args)



if __name__ == '__main__':

    main()
