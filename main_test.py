import argparse
import sqlalchemy as db

from peloton import PelotonProcessor


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS',
                    action='store_const', const=True, default=False,
                    help='check for new workouts on remote Peloton database')
args = parser.parse_args()


def main():   
    peloton_processor = PelotonProcessor()
    
    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton_processor.check_for_new_workouts()

    peloton_processor.print_processed_data_to_stdout()
    peloton_processor.print_pivot_tables_to_stdout()

    if peloton_processor.new_workouts:
        peloton_processor.write_csv_files()
        peloton_processor.processed_df.to_csv('processed_df.csv')

    

# def main():
#     sql_engine = db.create_engine(SQLITE_FILENAME)
#     processor = PelotonProcessor(sql_engine)
#     processor.check_for_new_workouts()
#     print(processor.processed_df)
#     print(processor.pivots.year_table)
#     print(processor.pivots.month_table)
#     print(processor.pivots.totals_table)

    # df = processor.processed_df
    # print(df)
    # # print(df.info())
    # df.to_csv('testtesddddasdfasdfddddssdt.csv')


    # processor.reprocess_json_data()

if __name__ == '__main__':
    main()




# def test_import() -> list[PelotonWorkoutData]:
#     with open('./data/workout_ids.txt', 'r') as f:
#         workout_id_list = [line.rstrip('\n') for line in f.readlines()]
#     with open('./data/workout_summaries.txt', 'r') as f:
#         summary_list = [ast.literal_eval(line) for line in f.readlines()]
#     with open('./data/workout_metrics.txt', 'r') as f:
#         metrics_list = [ast.literal_eval(line) for line in f.readlines()]

#     if len(workout_id_list) == len(summary_list) and len(workout_id_list) == len(metrics_list):
#         num_workouts = len(workout_id_list)
#     else:
#         raise WorkoutMismatchError('TXT files with workout IDs, summaries, and metrics are not all the same length!')

#     output_list=[]
#     for i in range(num_workouts):
#         workout_data = PelotonWorkoutData(
#             workout_id=workout_id_list[i],
#             summary_raw=summary_list[i],
#             metrics_raw=metrics_list[i],
#             summary=PelotonSummary.model_validate(summary_list[i]),
#             metrics=PelotonMetrics.model_validate(metrics_list[i])
#         )
#         output_list.append(workout_data)

#     return output_list

# def write_workouts_to_disk(workouts: list[PelotonWorkoutData]) -> None:
#     for workout in workouts:
#         with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
#             json.dump(workout.model_dump(), f, indent=4)