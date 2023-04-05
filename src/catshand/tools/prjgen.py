import argparse
from pathlib import Path
import json
import click
from catshand.utility import loggergen, configgen

def prjgen(args):
    print(args)
    rootdir = args.root_dir
    prj_n = args.project_name
    prjdir = Path(rootdir, prj_n)
    mat_dir = args.material_dir
    if mat_dir is not None:
        mat_dir = Path(mat_dir)
 
    if prjdir.is_dir():
        if not click.confirm(f'Project folder already exists, Continue?', default=True):
            return
    
    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')

    if not prjdir.is_dir():
        prjdir.mkdir(exist_ok = True, parents=True)
        logger.info(f'Craete the project folder: {prjdir}')
    else: 
        logger.info(f'Project folder exists')

    if not prjdir.joinpath('log').is_dir():
        prjdir.joinpath('log').mkdir(exist_ok = True, parents=True)
        logger.info(f'Craete the log folder: {prjdir.joinpath("log")}')
    else: 
        logger.info(f'Log folder exists')

    if not prjdir.joinpath('config').is_dir():
        prjdir.joinpath('config').mkdir(exist_ok = True, parents=True)
        logger.info(f'Craete the config folder: {prjdir.joinpath("config")}')
    else: 
        logger.info(f'Config folder exists')

    if not prjdir.joinpath('config', 'config.json').is_file():
        configgen(prjdir)
    else: 
        logger.info(f'Config.json exists')

    if mat_dir is None: return
    
    json_path = prjdir.joinpath('config', 'audt_config.json')

    if json_path.is_file():
        if click.confirm(f'audt_config.json already exists, Overwrite?', default=True):
            logger.info(f'Overwrite: {json_path}')
            templatejson_path = Path(__file__).parents[1].joinpath("config", "audt_config.json")
            with open(templatejson_path) as f:
                audt_config = json.load(f)

            audt_config['material']['root'] = str(mat_dir)

            with open(json_path, "w") as f:
                json.dump(audt_config, f, indent=2, sort_keys=False)

            logger.info(f'audt_config.json: {audt_config}')
    return

def add_subparser(subparsers):
    description = "prjgen creates the project folder"
    subparsers = subparsers.add_parser('prjgen', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-d', '--root_dir', type = str, required = True, help = 'directory for the project folder')
    required_group.add_argument('-n', '--project_name', type = str, required = True, help = 'project name (example: EP028)')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-m', '--material_dir', type = str, help = 'directory for the material folder')
    subparsers.set_defaults(func=prjgen)
    return