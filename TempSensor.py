
# Temperature sensor tools:
import argparse

from daemon import do_rundaemon



 



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

    return parser
    
    
    
    
    
    
if __name__=='__main__':
    main()

