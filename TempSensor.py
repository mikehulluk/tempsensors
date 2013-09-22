#! /usr/bin/python


# Temperature sensor tools:
import argparse

from action_daemon import do_rundaemon
from action_plot import do_plot
from action_import import do_importfromv1
from action_clear import do_clearall


 



def main():
    parser = build_argparser()
    args = parser.parse_args()
    
    # Run the choosen... function:
    args.func(args)
    
    
    



def build_argparser():
    parser = argparse.ArgumentParser(description='Temperature Sensor Project')
    
    subparsers = parser.add_subparsers(help='??')
    
    parser_daemon = subparsers.add_parser('daemon', help='??!?')
    parser_daemon.set_defaults(func=do_rundaemon)
    parser_daemon.add_argument('--dummy', dest='daemon_is_dummy', default=False, action='store_true', help='??')


    parser_plot = subparsers.add_parser('plot', help='??!?')
    parser_plot.set_defaults(func=do_plot)
    
    parser_clear = subparsers.add_parser('clear', help='??!?')
    parser_clear.set_defaults(func=do_clearall)

    parser_import = subparsers.add_parser('import', help='??!?')
    parser_import.set_defaults(func=do_importfromv1)


    return parser
    
    
    
    
    
    
if __name__=='__main__':
    main()

