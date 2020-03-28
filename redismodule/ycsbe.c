#include <stdint.h>
#include <assert.h>

#include "redismodule.h"

#define FIELD_NO 10
#define IDX_SET "indices"

static RedisModuleString *indices_set;
static RedisModuleString *f1;
static RedisModuleString *f2;
static RedisModuleString *f3;
static RedisModuleString *f4;
static RedisModuleString *f5;
static RedisModuleString *f6;
static RedisModuleString *f7;
static RedisModuleString *f8;
static RedisModuleString *f9;
static RedisModuleString *f10;

static unsigned long hash(const unsigned char *str, int len)
{
	unsigned long hash = 5381;
	int c, i;

	for (i=0;i<len;i++)
		hash = ((hash << 5) + hash) + str[i]; /* hash * 33 + c */

	return hash;
}

/*
 * key and 10 vals
 */
int YCSBE_insert(RedisModuleCtx *ctx, RedisModuleString **argv, int argc)
{

	long unsigned int len;
	const char *val;
	int res;
	RedisModuleKey *key, *indices_key;
	double score;

	RedisModule_AutoMemory(ctx);

	assert(argc == 2 + FIELD_NO); // op name + key +  FIELD_NO*vals

	// Add to hashmap
	key = RedisModule_OpenKey(ctx,argv[1],REDISMODULE_WRITE);
	res = RedisModule_HashSet(key,REDISMODULE_HASH_NONE,
			f1, argv[2], // field 1
			f2, argv[3], // field 2
			f3, argv[4], // field 3
			f4, argv[5], // field 4
			f5, argv[6], // field 5
			f6, argv[7], // field 6
			f7, argv[8], // field 7
			f8, argv[9], // field 8
			f9, argv[10], // field 9
			f10, argv[11], // field 10
			NULL);
	if (res < 0) {
		size_t len;
		const char * missing = RedisModule_StringPtrLen(argv[1],&len);
		printf("ret = %d. I didn't manage to add %s\n", res, missing);
		RedisModule_ReplyWithSimpleString(ctx, "OK");
		return REDISMODULE_OK;
	}

	// Add to ordered set
	indices_key = RedisModule_OpenKey(ctx, indices_set, REDISMODULE_WRITE);
	val = RedisModule_StringPtrLen(argv[1], &len);
	score = hash(val, len);
	res = RedisModule_ZsetAdd(indices_key, score, argv[1], NULL);
	assert(res == REDISMODULE_OK);

	RedisModule_ReplyWithSimpleString(ctx, "OK");
	return REDISMODULE_OK;
}

/*
 * starting key and count
 */
int YCSBE_scan(RedisModuleCtx *ctx, RedisModuleString **argv, int argc)
{
	int res, i;
	long long count;
	double score;
	long unsigned int len;
	const char *str_val;
	RedisModuleKey *key, *indices_key;
	RedisModuleString *val;
	RedisModuleString *val1, *val2, *val3, *val4, *val5, *val6, *val7, *val8,
					  *val9, *val10;

	RedisModule_AutoMemory(ctx);

	assert(argc = 3); // op + key + count;

	// Get count;
	RedisModule_StringToLongLong(argv[2], &count);

	indices_key = RedisModule_OpenKey(ctx, indices_set, REDISMODULE_WRITE);

	str_val = RedisModule_StringPtrLen(argv[1], &len);
	score = hash(str_val, len);
	res = RedisModule_ZsetFirstInScoreRange(indices_key,
			score, REDISMODULE_POSITIVE_INFINITE, 0, 0);
	val = RedisModule_ZsetRangeCurrentElement(indices_key, &score);
	if (!val) {
		RedisModule_ReplyWithNull(ctx);
		goto OUT;
	}

	RedisModule_ReplyWithArray(ctx, count);
	for (i=0;i<count;i++) {
		val = RedisModule_ZsetRangeCurrentElement(indices_key, &score);
		// Get the data from the hashmap
		key = RedisModule_OpenKey(ctx, val, REDISMODULE_READ);
		res = RedisModule_HashGet(key, REDISMODULE_HASH_NONE,
				f1, &val1,
				f2, &val2,
				f3, &val3,
				f4, &val4,
				f5, &val5,
				f6, &val6,
				f7, &val7,
				f8, &val8,
				f9, &val9,
				f10, &val10,
				NULL);

		if (res != REDISMODULE_OK) {
			size_t len;
			const char * missing = RedisModule_StringPtrLen(val,&len);
			printf("I didn't find %s\n", missing);
		}
		assert(res == REDISMODULE_OK);

		RedisModule_ReplyWithArray(ctx, FIELD_NO);
		RedisModule_ReplyWithString(ctx, val1);
		RedisModule_ReplyWithString(ctx, val2);
		RedisModule_ReplyWithString(ctx, val3);
		RedisModule_ReplyWithString(ctx, val4);
		RedisModule_ReplyWithString(ctx, val5);
		RedisModule_ReplyWithString(ctx, val6);
		RedisModule_ReplyWithString(ctx, val7);
		RedisModule_ReplyWithString(ctx, val8);
		RedisModule_ReplyWithString(ctx, val9);
		RedisModule_ReplyWithString(ctx, val10);

		res = RedisModule_ZsetRangeNext(indices_key);
		if (res == 0)
			break;
	}
	for (;i<count;i++)
		RedisModule_ReplyWithNull(ctx);

OUT:
	return REDISMODULE_OK;
}

int RedisModule_OnLoad(RedisModuleCtx *ctx, RedisModuleString **argv, int argc)
{
	if (RedisModule_Init(ctx, "ycsbe", 1, REDISMODULE_APIVER_1)
			== REDISMODULE_ERR) return REDISMODULE_ERR;

	const char *strflags = "write";
	if (RedisModule_CreateCommand(ctx,"ycsbe.insert",
				YCSBE_insert, strflags,
				1, 1, -1) == REDISMODULE_ERR)
		return REDISMODULE_ERR;

	if (RedisModule_CreateCommand(ctx,"ycsbe.scan",
				YCSBE_scan, strflags,
				1, 1, -1) == REDISMODULE_ERR)
		return REDISMODULE_ERR;

	indices_set = RedisModule_CreateString(ctx, IDX_SET, 7);
	f1 = RedisModule_CreateString(ctx, "f1", 2);
	f2 = RedisModule_CreateString(ctx, "f2", 2);
	f3 = RedisModule_CreateString(ctx, "f3", 2);
	f4 = RedisModule_CreateString(ctx, "f4", 2);
	f5 = RedisModule_CreateString(ctx, "f5", 2);
	f6 = RedisModule_CreateString(ctx, "f6", 2);
	f7 = RedisModule_CreateString(ctx, "f7", 2);
	f8 = RedisModule_CreateString(ctx, "f8", 2);
	f9 = RedisModule_CreateString(ctx, "f9", 2);
	f10 = RedisModule_CreateString(ctx, "f10", 3);


	return REDISMODULE_OK;
}
